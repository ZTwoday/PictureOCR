from PySide6.QtGui import QIcon

from core import icons


def test_load_app_icon_nonnull(app):
    icon = icons.load_app_icon()
    assert isinstance(icon, QIcon)
    assert not icon.isNull()
    pm = icon.pixmap(64, 64)
    assert not pm.isNull()
    assert pm.width() == 64


def test_load_tray_icon_nonnull(app):
    icon = icons.load_tray_icon()
    assert isinstance(icon, QIcon)
    assert not icon.isNull()
    assert not icon.pixmap(16, 16).isNull()
