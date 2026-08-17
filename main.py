import os
import sys
import uuid
from datetime import datetime

from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMenu, QSystemTrayIcon

from capture.overlay import CaptureOverlay
from capture.screen import save_pixmap
from core.config import data_dir, load_config
from core.hotkey import GlobalHotkey
from core.icons import load_app_icon, load_tray_icon
from ocr.manager import OCRManager
from ui.main_window import MainWindow
from ui.screenshot_preview import ScreenshotPreview
from ui.settings_dialog import SettingsDialog


def _make_tray_icon() -> QIcon:
    return load_tray_icon()


APP_SOCKET = "picture-ocr-app"


def _wake_existing_instance(socket_name: str = APP_SOCKET) -> bool:
    """True if another instance is running; ask it to show its window."""
    socket = QLocalSocket()
    socket.connectToServer(socket_name)
    if not socket.waitForConnected(400):
        return False
    socket.write(b"show")
    socket.waitForBytesWritten(300)
    return True


class OcrApp(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.overlay = CaptureOverlay()
        self.manager = OCRManager(self)
        self.window = MainWindow()
        self.settings_dialog = None
        self._pending_image = None
        self._enhance_requested = False
        self._capture_mode = "ocr"
        self._overlay_active = False
        self._hotkey = GlobalHotkey(self)

        self.tray = QSystemTrayIcon(_make_tray_icon(), self)
        self.tray.setToolTip("截图识字")
        self.tray.activated.connect(self._on_tray_activated)
        self._build_tray_menu()
        self.tray.show()

        self._server = QLocalServer(self)
        self._server.removeServer(APP_SOCKET)
        self._server.listen(APP_SOCKET)
        self._server.newConnection.connect(self._on_second_launch)

        self._wire()

    def _build_tray_menu(self):
        menu = QMenu()
        menu.addAction("识别文字", self.start_capture)
        menu.addAction("截图", self.start_shot)
        menu.addAction("打开主窗口", self.show_window)
        menu.addAction("设置", self.open_settings)
        menu.addAction("退出", self.app.quit)
        self.tray.setContextMenu(menu)

    def _wire(self):
        self.overlay.region_selected.connect(self._on_region_selected)
        self.overlay.cancelled.connect(self._on_capture_cancelled)
        self.window.capture_requested.connect(self.start_capture)
        self.window.shot_requested.connect(self.start_shot)
        self.window.enhance_requested.connect(self._enhance)
        self.manager.finished.connect(self._on_ocr_finished)
        self.manager.error.connect(self._show_error)

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_window()

    def _on_second_launch(self):
        conn = self._server.nextPendingConnection()
        conn.readyRead.connect(lambda c=conn: self._activate_from(c))
        conn.disconnected.connect(conn.deleteLater)

    def _activate_from(self, conn):
        if bytes(conn.readAll()) == b"show":
            self.show_window()
        conn.deleteLater()

    def show_window(self):
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _show_error(self, msg):
        self.window.show_error(msg)
        if not self._overlay_active:
            self.show_window()

    def start_capture(self):
        self._capture_mode = "ocr"
        self._begin_capture()

    def start_shot(self):
        self._capture_mode = "shot"
        self._begin_capture()

    def _on_capture_cancelled(self):
        self._overlay_active = False
        self.show_window()

    def _begin_capture(self):
        if self._overlay_active:
            return
        self._overlay_active = True
        self.window.hide()
        # grabWindow(0) races the DWM compositor: right after hide() the
        # window can still be present in the captured frame, blocking the
        # region the user wants. Measured ~365ms for this window to fully
        # clear on a 1080p display, so wait 500ms for it to be gone.
        QTimer.singleShot(500, self.overlay.start)

    def _on_region_selected(self, x, y, w, h):
        self._overlay_active = False
        pixmap = self.overlay.crop_region(x, y, w, h)
        if self._capture_mode == "shot":
            self._handle_shot(pixmap)
            return
        images_dir = os.path.join(data_dir(), "images")
        os.makedirs(images_dir, exist_ok=True)
        image_path = os.path.join(images_dir, f"{uuid.uuid4().hex}.png")
        save_pixmap(pixmap, image_path)
        self._pending_image = image_path
        engine = load_config().get("default_engine", "rapid")
        self.manager.recognize_async(image_path, engine)

    def _handle_shot(self, pixmap):
        preview = ScreenshotPreview(pixmap, self.window)
        if preview.exec() != QDialog.DialogCode.Accepted:
            self.show_window()
            return
        if preview.choice == "continue":
            self.start_shot()
        elif preview.choice == "copy":
            QApplication.clipboard().setPixmap(pixmap)
            self.tray.showMessage("截图", "已复制到剪贴板",
                                  QSystemTrayIcon.MessageIcon.Information, 2000)
        elif preview.choice == "save":
            self._save_shot(pixmap)

    def _save_shot(self, pixmap):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default = os.path.join(os.path.expanduser("~"), "Pictures", f"截图_{timestamp}.png")
        path, _ = QFileDialog.getSaveFileName(self.window, "保存截图", default, "PNG 图片 (*.png)")
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        save_pixmap(pixmap, path)
        self.tray.showMessage("截图", f"已保存：{path}",
                              QSystemTrayIcon.MessageIcon.Information, 2500)

    def _on_ocr_finished(self, text, engine):
        note = None
        if self._enhance_requested:
            self._enhance_requested = False
            if engine != "baidu":
                note = "百度不可用，已回退本地识别"
        self.window.show_result(text, engine, note=note)
        if not self._overlay_active:
            self.show_window()

    def _enhance(self):
        if self._pending_image is None:
            return
        self._enhance_requested = True
        self.window.set_busy(True)
        self.manager.recognize_async(self._pending_image, "baidu")

    def open_settings(self):
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self.window)
        self.settings_dialog.exec()
        config = load_config()
        self._apply_hotkey(config.get("hotkey", "Ctrl+Alt+A"))

    def _apply_hotkey(self, spec: str):
        self._hotkey.unregister()
        if not self._hotkey.register(int(self.window.winId()), spec, self.start_capture):
            print(f"WARNING: global hotkey '{spec}' failed to register (possibly in use)",
                  file=sys.stderr)
            self.tray.showMessage("热键注册失败",
                                  f"全局热键 {spec} 可能被其他程序占用，请使用主窗口按钮",
                                  QSystemTrayIcon.MessageIcon.Warning)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("截图识字")
    app.setWindowIcon(load_app_icon())
    app.setQuitOnLastWindowClosed(False)

    if _wake_existing_instance():
        tray = QSystemTrayIcon(_make_tray_icon(), app)
        tray.show()
        tray.showMessage("截图识字", "应用已在运行，已打开主窗口",
                         QSystemTrayIcon.Information, 2500)
        QTimer.singleShot(2500, app.quit)
        return sys.exit(app.exec())

    ocr_app = OcrApp(app)
    ocr_app.window.show()
    ocr_app._apply_hotkey(load_config().get("hotkey", "Ctrl+Alt+A"))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
