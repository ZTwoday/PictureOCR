from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                               QMainWindow, QPushButton, QVBoxLayout, QWidget)

from storage.history import load_history, delete_entry, clear_history, default_history_path


class HistoryWindow(QMainWindow):
    need_ocr = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("识别历史")
        self.resize(560, 420)

        central = QWidget()
        layout = QVBoxLayout(central)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        buttons = QHBoxLayout()
        self.capture_button = QPushButton("框选截图")
        self.delete_button = QPushButton("删除选中")
        self.clear_button = QPushButton("清空全部")
        buttons.addWidget(self.capture_button)
        buttons.addWidget(self.delete_button)
        buttons.addWidget(self.clear_button)
        buttons.addStretch()
        layout.addLayout(buttons)
        self.setCentralWidget(central)

        self.capture_button.clicked.connect(self.need_ocr.emit)
        self.delete_button.clicked.connect(self._delete_selected)
        self.clear_button.clicked.connect(self._clear_all)

    def refresh(self):
        self.list_widget.clear()
        for entry in load_history(default_history_path()):
            preview = (entry.text.splitlines() or [""])[0] or "(空)"
            label = f"{entry.timestamp}\n{preview}\n引擎:{entry.engine}"
            item = QListWidgetItem(label)
            if entry.image_path:
                pixmap = QPixmap(entry.image_path).scaledToWidth(48)
                if not pixmap.isNull():
                    item.setIcon(pixmap)
            item.setData(Qt.UserRole, entry.id)
            self.list_widget.addItem(item)

    def _delete_selected(self):
        item = self.list_widget.currentItem()
        if item is not None:
            delete_entry(item.data(Qt.UserRole), default_history_path())
            self.refresh()

    def _clear_all(self):
        clear_history(default_history_path())
        self.refresh()
