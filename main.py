import os
import sys
import uuid
from datetime import datetime

from PySide6.QtCore import QObject, QSharedMemory, Qt, QThread, QTimer
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from capture.overlay import CaptureOverlay
from capture.screen import capture_region, save_pixmap
from core.config import data_dir, load_config
from core.hotkey import GlobalHotkey
from ocr.manager import OCRManager
from storage.history import HistoryEntry, add_entry
from ui.history_window import HistoryWindow
from ui.result_popup import ResultPopup
from ui.settings_dialog import SettingsDialog


def _make_tray_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#2d7ff9"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(2, 2, 28, 28, 7, 7)
    painter.end()
    return QIcon(pixmap)


class SingleInstanceGuard:
    _KEY = "com.picture-ocr.singleton"

    def __init__(self):
        self._shm = QSharedMemory(self._KEY)
        if self._shm.attach():
            self.is_primary = False
            return
        self.is_primary = self._shm.create(1)


class OcrApp(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.overlay = CaptureOverlay()
        self.manager = OCRManager(self)
        self.popup = ResultPopup()
        self.history_window = HistoryWindow()
        self.settings_dialog = None
        self._pending_image = None
        self._last_entry = None
        self._enhance_requested = False
        self._hotkey = GlobalHotkey(self)

        self.tray = QSystemTrayIcon(_make_tray_icon(), self)
        self.tray.setToolTip("OCR 截图识字")
        self._build_tray_menu()
        self.tray.show()

        self._wire()

    def _build_tray_menu(self):
        menu = QMenu()
        menu.addAction("框选截图", self.start_capture)
        menu.addAction("打开历史", self.history_window.show)
        menu.addAction("设置", self.open_settings)
        menu.addAction("退出", self.app.quit)
        self.tray.setContextMenu(menu)

    def _wire(self):
        self.overlay.region_selected.connect(self._on_region_selected)
        self.overlay.cancelled.connect(self.history_window.show)
        self.history_window.need_ocr.connect(self.start_capture)
        self.manager.finished.connect(self._on_ocr_finished)
        self.manager.error.connect(self._show_error)

    def _show_error(self, msg):
        self.popup.show_result(msg, "错误", on_enhance=None)

    def start_capture(self):
        self.history_window.hide()
        self.popup.hide()
        self.overlay.start()

    def _on_region_selected(self, x, y, w, h):
        pixmap = capture_region(x, y, w, h)
        images_dir = os.path.join(data_dir(), "images")
        os.makedirs(images_dir, exist_ok=True)
        image_path = os.path.join(images_dir, f"{uuid.uuid4().hex}.png")
        save_pixmap(pixmap, image_path)
        self._pending_image = image_path
        engine = load_config().get("default_engine", "rapid")
        self.manager.recognize_async(image_path, engine)

    def _on_ocr_finished(self, text, engine):
        entry = HistoryEntry(id=uuid.uuid4().hex,
                             timestamp=datetime.now().isoformat(timespec="seconds"),
                             image_path=self._pending_image, text=text, engine=engine)
        add_entry(entry)
        self._last_entry = entry
        self.history_window.refresh()
        note = None
        if self._enhance_requested:
            self._enhance_requested = False
            if engine != "baidu":
                note = "百度不可用，已回退本地识别"
        self.popup.show_result(text, engine, on_enhance=self._enhance, note=note)

    def _enhance(self):
        if self._pending_image is None:
            return
        self.popup.setWindowTitle("云端增强识别中…")
        self._enhance_requested = True
        self.manager.recognize_async(self._pending_image, "baidu")

    def open_settings(self):
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self.history_window)
        self.settings_dialog.exec()
        config = load_config()
        self._apply_hotkey(config.get("hotkey", "Ctrl+Alt+A"))

    def _apply_hotkey(self, spec: str):
        self._hotkey.unregister()
        if not self._hotkey.register(int(self.history_window.winId()), spec, self.start_capture):
            print(f"WARNING: global hotkey '{spec}' failed to register (possibly in use)", file=sys.stderr)
            self.tray.showMessage(
                "热键注册失败",
                f"全局热键 {spec} 可能被其他程序占用，请使用托盘或窗口按钮触发",
                QSystemTrayIcon.MessageIcon.Warning,
            )


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    guard = SingleInstanceGuard()
    if not guard.is_primary:
        tray = QSystemTrayIcon(_make_tray_icon(), app)
        tray.show()
        tray.showMessage("OCR 截图识字", "应用已在运行，无需重复启动",
                         QSystemTrayIcon.Information, 3000)
        QTimer.singleShot(3500, app.quit)
        sys.exit(app.exec())
    ocr_app = OcrApp(app)
    ocr_app._apply_hotkey(load_config().get("hotkey", "Ctrl+Alt+A"))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
