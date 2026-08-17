from PySide6.QtGui import QIcon, QImage, QPixmap

from core.icons import BUTTON_ICONS, load_button_icon, load_source_icon


def _pixmap_icon(icon: QIcon) -> QPixmap:
    return icon.pixmap(256, 256)


def _alpha_bbox(pm: QPixmap) -> tuple:
    img = pm.toImage().convertToFormat(QImage.Format_ARGB32)
    xs, ys = [], []
    for y in range(img.height()):
        for x in range(img.width()):
            if img.pixelColor(x, y).alpha() > 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def test_all_button_icons_are_defined(app):
    assert set(BUTTON_ICONS) == {"recognize", "shot", "save", "copy"}


def test_load_button_icon_returns_nonnull_for_all(app):
    for key in BUTTON_ICONS:
        assert not load_button_icon(key).isNull(), key


def test_load_source_icon_returns_nonnull_for_all(app):
    for key in BUTTON_ICONS:
        assert not load_source_icon(key).isNull(), key


def test_button_icons_are_tinted_white(app):
    # Blue buttons need white ink: no opaque pixel may stay dark.
    for key in BUTTON_ICONS:
        pm = _pixmap_icon(load_button_icon(key))
        img = pm.toImage().convertToFormat(QImage.Format_ARGB32)
        for y in range(img.height()):
            for x in range(img.width()):
                c = img.pixelColor(x, y)
                if c.alpha() > 0:
                    assert c.red() == 255 and c.green() == 255 and c.blue() == 255, key


def test_shot_icon_white_backdrop_removed(app):
    # The shot icon source is a white-tile asset; the white backdrop must become
    # transparent so the icon isn't a solid white square on the blue button.
    pm = _pixmap_icon(load_button_icon("shot"))
    img = pm.toImage().convertToFormat(QImage.Format_ARGB32)
    w, h = img.width(), img.height()
    corner = img.pixelColor(0, 0)
    assert corner.alpha() == 0
    assert _alpha_bbox(pm) is not None


def test_source_icons_keep_original_dark_ink(app):
    # Light preview buttons keep the original dark line art.
    pm = _pixmap_icon(load_source_icon("save"))
    img = pm.toImage().convertToFormat(QImage.Format_ARGB32)
    has_dark = any(
        img.pixelColor(x, y).alpha() > 0 and img.pixelColor(x, y).lightness() < 128
        for y in range(img.height())
        for x in range(img.width())
    )
    assert has_dark
