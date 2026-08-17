from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                               QPlainTextEdit, QPushButton, QVBoxLayout, QWidget)

from core.icons import load_button_icon


class MainWindow(QMainWindow):
    """Single main window: launch a capture and show the recognized text."""

    capture_requested = Signal()
    enhance_requested = Signal()
    shot_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("截图识字")
        self.resize(540, 460)
        self._original_text = None
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        top = QHBoxLayout()
        self.capture_button = QPushButton()
        self.capture_button.setObjectName("captureButton")
        self.capture_button.setToolTip("识别文字：框选屏幕区域，识别其中的文字")
        self.capture_button.setCursor(Qt.PointingHandCursor)
        self.capture_button.setIcon(load_button_icon("recognize"))
        self.capture_button.setIconSize(QSize(32, 32))
        self.capture_button.clicked.connect(self.capture_requested.emit)
        top.addWidget(self.capture_button)

        self.shot_button = QPushButton()
        self.shot_button.setObjectName("captureButton")
        self.shot_button.setToolTip("截图：框选屏幕区域，保存或复制为图片")
        self.shot_button.setCursor(Qt.PointingHandCursor)
        self.shot_button.setIcon(load_button_icon("shot"))
        self.shot_button.setIconSize(QSize(32, 32))
        self.shot_button.clicked.connect(self.shot_requested.emit)
        top.addWidget(self.shot_button)
        top.addStretch()
        layout.addLayout(top)

        self.hint_label = QLabel("按 Ctrl+Alt+A 或点击上方图标：识别文字 / 截图")
        self.hint_label.setObjectName("hintLabel")
        self.hint_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.hint_label)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setObjectName("resultText")
        self.text_edit.setPlaceholderText("识别结果显示在这里，可直接修改后复制")
        layout.addWidget(self.text_edit, 1)

        self.note_label = QLabel()
        self.note_label.setObjectName("noteLabel")
        self.note_label.hide()
        layout.addWidget(self.note_label)

        bottom = QHBoxLayout()
        self.engine_label = QLabel("引擎：—")
        self.engine_label.setObjectName("engineLabel")
        self.restore_button = QPushButton("还原")
        self.copy_button = QPushButton("复制全部")
        self.enhance_button = QPushButton("云端增强")
        self.restore_button.clicked.connect(self.restore_original)
        self.copy_button.clicked.connect(self.copy_all)
        self.enhance_button.clicked.connect(self.enhance_requested.emit)
        self.restore_button.setEnabled(False)
        self.enhance_button.setEnabled(False)
        bottom.addWidget(self.engine_label)
        bottom.addStretch()
        bottom.addWidget(self.restore_button)
        bottom.addWidget(self.copy_button)
        bottom.addWidget(self.enhance_button)
        layout.addLayout(bottom)

        self.setCentralWidget(central)

    def copy_all(self):
        QApplication.clipboard().setText(self.text_edit.toPlainText())

    def restore_original(self):
        if self._original_text is None:
            return
        self.text_edit.setPlainText(self._original_text)

    def show_result(self, text, engine, note=None):
        self.text_edit.setPlainText(text)
        self._original_text = text
        self.engine_label.setText(f"引擎：{engine}")
        self.hint_label.hide()
        self.capture_button.setEnabled(True)
        self.shot_button.setEnabled(True)
        self.copy_button.setEnabled(True)
        self.enhance_button.setEnabled(True)
        self.restore_button.setEnabled(True)
        if note:
            self.note_label.setText(note)
            self.note_label.show()
        else:
            self.note_label.hide()

    def show_error(self, msg):
        self.text_edit.setPlainText(msg)
        self._original_text = None
        self.engine_label.setText("引擎：错误")
        self.hint_label.hide()
        self.note_label.hide()
        self.capture_button.setEnabled(True)
        self.shot_button.setEnabled(True)
        self.copy_button.setEnabled(False)
        self.restore_button.setEnabled(False)

    def set_busy(self, busy):
        self.capture_button.setEnabled(not busy)
        self.shot_button.setEnabled(not busy)
        self.enhance_button.setEnabled(not busy)
        self.restore_button.setEnabled(not busy)
        if busy:
            self.hint_label.setText("识别中…")
            self.hint_label.show()

    def _apply_style(self):
        self.setStyleSheet(
            """
            QMainWindow { background: #f5f6f8; }
            #captureButton {
                background: #2d7ff9; color: white; border: none; border-radius: 8px;
                padding: 14px; font-size: 16px; font-weight: 600;
            }
            #captureButton:hover { background: #1f6fe0; }
            #captureButton:pressed { background: #1a5fc8; }
            #captureButton:disabled { background: #a8c6f2; }
            #hintLabel { color: #8a8f98; font-size: 13px; }
            #resultText {
                background: white; border: 1px solid #e0e3e8; border-radius: 8px;
                padding: 10px; font-size: 14px; color: #222;
            }
            #noteLabel { color: #c0392b; font-size: 12px; }
            #engineLabel { color: #8a8f98; font-size: 12px; }
            QPushButton {
                background: white; border: 1px solid #d0d4da; border-radius: 6px;
                padding: 6px 14px; font-size: 13px; color: #333;
            }
            QPushButton:hover { background: #f0f2f5; }
            QPushButton:pressed { background: #e4e7eb; }
            QPushButton:disabled { color: #b0b4ba; background: #f5f6f8; }
            """
        )
