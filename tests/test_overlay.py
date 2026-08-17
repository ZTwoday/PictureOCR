from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from capture.overlay import CaptureOverlay, build_crosshair_cursor
from capture.screen import normalize_rect


def test_normalize_rect_drag_right_down():
    assert normalize_rect(10, 20, 60, 80) == (10, 20, 50, 60)


def test_normalize_rect_drag_backwards():
    assert normalize_rect(60, 80, 10, 20) == (10, 20, 50, 60)


def test_normalize_rect_zero_size():
    assert normalize_rect(10, 20, 10, 20) == (10, 20, 0, 0)


def test_crosshair_cursor_is_custom_bitmap(app):
    cursor = build_crosshair_cursor()
    assert cursor.shape() == Qt.BitmapCursor
    assert not cursor.pixmap().isNull()


def test_overlay_uses_custom_crosshair_cursor(app):
    overlay = CaptureOverlay()
    assert overlay.cursor().shape() == Qt.BitmapCursor


def test_crop_region_cuts_from_frozen_frame(app):
    overlay = CaptureOverlay()
    img = QImage(200, 100, QImage.Format_ARGB32)
    img.fill(0xFF112233)
    overlay._frozen = QPixmap.fromImage(img)
    cropped = overlay.crop_region(10, 20, 50, 60)
    assert not cropped.isNull()
    assert cropped.width() == 50
    assert cropped.height() == 60
