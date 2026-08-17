from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog

from ui.screenshot_preview import ScreenshotPreview


def _pixmap(w=100, h=60):
    pm = QPixmap(w, h)
    pm.fill(Qt.white)
    return pm


def test_preview_buttons_are_icon_only_with_tooltips(app):
    dialog = ScreenshotPreview(_pixmap())
    assert dialog.continue_button.text() == ""
    assert dialog.save_button.text() == ""
    assert dialog.copy_button.text() == ""
    assert not dialog.continue_button.icon().isNull()
    assert not dialog.save_button.icon().isNull()
    assert not dialog.copy_button.icon().isNull()
    assert "继续截图" in dialog.continue_button.toolTip()
    assert "保存" in dialog.save_button.toolTip()
    assert "复制到剪贴板" in dialog.copy_button.toolTip()


def test_continue_button_sets_choice_continue(app):
    dialog = ScreenshotPreview(_pixmap())
    dialog._choose_continue()
    assert dialog.choice == "continue"
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_copy_button_sets_choice_copy(app):
    dialog = ScreenshotPreview(_pixmap())
    dialog._choose_copy()
    assert dialog.choice == "copy"
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_save_button_sets_choice_save(app):
    dialog = ScreenshotPreview(_pixmap())
    dialog._choose_save()
    assert dialog.choice == "save"
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_large_image_is_scaled_down_in_preview(app):
    dialog = ScreenshotPreview(_pixmap(2000, 1000))
    pm = dialog.image_label.pixmap()
    assert pm is not None
    assert pm.width() <= 720
