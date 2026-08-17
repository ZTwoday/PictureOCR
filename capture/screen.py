from PySide6.QtGui import QPixmap


def normalize_rect(x1: int, y1: int, x2: int, y2: int) -> tuple[int, int, int, int]:
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    return left, top, right - left, bottom - top


def save_pixmap(pixmap: QPixmap, path: str) -> None:
    pixmap.save(path)
