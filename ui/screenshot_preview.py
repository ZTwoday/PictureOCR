from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from core.icons import load_source_icon

MAX_PREVIEW_W = 720
MAX_PREVIEW_H = 480


class ScreenshotPreview(QDialog):
    """Show a captured region and let the user save it or copy it to the clipboard."""

    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.choice = None
        self.setWindowTitle("截图预览")
        self.setModal(True)
        self._build_ui(pixmap)

    def _build_ui(self, pixmap):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        buttons = QHBoxLayout()
        self.continue_button = QPushButton()
        self.continue_button.setToolTip("继续截图：再框选一块区域，无需返回主窗口")
        self.continue_button.setIcon(load_source_icon("shot"))
        self.continue_button.setIconSize(QSize(22, 22))
        self.save_button = QPushButton()
        self.save_button.setToolTip("保存：将截图保存为图片")
        self.save_button.setIcon(load_source_icon("save"))
        self.save_button.setIconSize(QSize(22, 22))
        self.copy_button = QPushButton()
        self.copy_button.setToolTip("复制到剪贴板：复制截图到剪贴板")
        self.copy_button.setIcon(load_source_icon("copy"))
        self.copy_button.setIconSize(QSize(22, 22))
        self.continue_button.clicked.connect(self._choose_continue)
        self.save_button.clicked.connect(self._choose_save)
        self.copy_button.clicked.connect(self._choose_copy)
        buttons.addWidget(self.continue_button)
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.copy_button)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        if pixmap.isNull():
            self.image_label.setText("预览失败：未获取到图像")
        else:
            self.image_label.setPixmap(self._scaled(pixmap))
        layout.addWidget(self.image_label, 1)

    @staticmethod
    def _scaled(pixmap: QPixmap) -> QPixmap:
        if pixmap.width() <= MAX_PREVIEW_W and pixmap.height() <= MAX_PREVIEW_H:
            return pixmap
        return pixmap.scaled(MAX_PREVIEW_W, MAX_PREVIEW_H,
                             Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def _choose_continue(self):
        self.choice = "continue"
        self.accept()

    def _choose_save(self):
        self.choice = "save"
        self.accept()

    def _choose_copy(self):
        self.choice = "copy"
        self.accept()
