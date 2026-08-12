"""Runtime icon loading: app icon (windows/taskbar) and white tray icon."""
import os

from PySide6.QtGui import QIcon, QPixmap

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "assets", "icons")


def load_app_icon() -> QIcon:
    icon = QIcon()
    pixmap = QPixmap(os.path.join(ASSETS_DIR, "app_icon.png"))
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
