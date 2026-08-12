from PySide6.QtGui import QGuiApplication, QPixmap
from PySide6.QtCore import QRect


def normalize_rect(x1: int, y1: int, x2: int, y2: int) -> tuple[int, int, int, int]:
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    return left, top, right - left, bottom - top


def capture_region(x: int, y: int, w: int, h: int) -> QPixmap:
    screen = QGuiApplication.primaryScreen()
    full = screen.grabWindow(0)
    return full.copy(QRect(x, y, w, h))


def save_pixmap(pixmap: QPixmap, path: str) -> None:
    pixmap.save(path)
