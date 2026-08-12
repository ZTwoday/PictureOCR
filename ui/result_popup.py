from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPlainTextEdit, QPushButton,
                               QVBoxLayout, QWidget, QApplication)


class ResultPopup(QWidget):
    close_requested = Signal()

    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowTitle("识别结果")
        self.resize(360, 240)

        layout = QVBoxLayout(self)
        self.engine_label = QLabel()
        layout.addWidget(self.engine_label)

        self.note_label = QLabel()
        self.note_label.setStyleSheet("color: #c0392b;")
        self.note_label.hide()
        layout.addWidget(self.note_label)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        buttons = QHBoxLayout()
        self.copy_button = QPushButton("复制全部")
        self.enhance_button = QPushButton("云端增强")
        self.close_button = QPushButton("关闭")
        buttons.addWidget(self.copy_button)
        buttons.addWidget(self.enhance_button)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

        self._on_enhance = None
        self.copy_button.clicked.connect(self.copy_all)
        self.enhance_button.clicked.connect(self._enhance)
        self.close_button.clicked.connect(self.close)

    def show_result(self, text: str, engine: str, on_enhance=None, note=None):
        self.text_edit.setPlainText(text)
        self.engine_label.setText(f"引擎：{engine}")
        if note:
            self.note_label.setText(note)
            self.note_label.show()
        else:
            self.note_label.hide()
        self._on_enhance = on_enhance
        self.enhance_button.setVisible(on_enhance is not None)
        self.show()
        self.raise_()
        self.activateWindow()

    def copy_all(self):
        QApplication.clipboard().setText(self.text_edit.toPlainText())

    def _enhance(self):
        if self._on_enhance:
            self._on_enhance()
