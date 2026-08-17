"""Runtime icon loading: app icon (windows/taskbar), white tray icon, button icons."""
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QIcon, QPixmap

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "assets", "icons")
MATERIALS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "素材")

# (source filename, drop_white_bg) — 截图 icon is a white-tile style asset and
# needs its backdrop removed before tinting.
BUTTON_ICONS = {
    "recognize": ("文字识别图标.png", False),
    "shot": ("截图图标.png", True),
    "save": ("保存图标.png", False),
    "copy": ("复制图标.svg", False),
}


def load_app_icon() -> QIcon:
    """Window/taskbar icon. White line drawing so it is visible on a dark taskbar."""
    icon = QIcon()
    for name in ("app_icon_white.png", "tray_icon_32.png", "tray_icon_16.png"):
        pixmap = QPixmap(os.path.join(ASSETS_DIR, name))
        if not pixmap.isNull():
            icon.addPixmap(pixmap)
    return icon


def load_tray_icon() -> QIcon:
    icon = QIcon()
    for name in ("tray_icon_16.png", "tray_icon_32.png"):
        pixmap = QPixmap(os.path.join(ASSETS_DIR, name))
        if not pixmap.isNull():
            icon.addPixmap(pixmap)
    return icon


def _load_source_image(filename: str) -> QImage:
    """Load a button-icon source (PNG or SVG) into a QImage."""
    path = os.path.join(MATERIALS_DIR, filename)
    if filename.lower().endswith(".svg"):
        from PySide6.QtGui import QPainter
        from PySide6.QtSvg import QSvgRenderer
        renderer = QSvgRenderer(path)
        img = QImage(256, 256, QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        painter = QPainter(img)
        renderer.render(painter)
        painter.end()
        return img
    return QPixmap(path).toImage()


def _to_white_ink(img: QImage, drop_white_bg: bool = False) -> QImage:
    """Recolor ink to white, preserving alpha. Optionally drop a near-white backdrop."""
    out = img.convertToFormat(QImage.Format_ARGB32)
    for y in range(out.height()):
        for x in range(out.width()):
            color = out.pixelColor(x, y)
            if color.alpha() == 0:
                continue
            if drop_white_bg and color.red() > 200 and color.green() > 200 and color.blue() > 200:
                out.setPixelColor(x, y, QColor(0, 0, 0, 0))
                continue
            out.setPixelColor(x, y, QColor(255, 255, 255, color.alpha()))
    return out


def load_button_icon(key: str) -> QIcon:
    """White-ink icon for the blue main-window buttons."""
    filename, drop_white = BUTTON_ICONS[key]
    white = _to_white_ink(_load_source_image(filename), drop_white_bg=drop_white)
    return QIcon(QPixmap.fromImage(white))


def load_source_icon(key: str) -> QIcon:
    """Original-ink icon for the light preview buttons."""
    filename, _ = BUTTON_ICONS[key]
    return QIcon(QPixmap.fromImage(_load_source_image(filename)))
