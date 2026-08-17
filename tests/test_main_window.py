from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def test_show_result_updates_text_and_engine(app):
    window = MainWindow()
    window.show_result("第一行\nsecond line", "rapid")
    assert window.text_edit.toPlainText() == "第一行\nsecond line"
    assert "rapid" in window.engine_label.text()
    assert window.hint_label.isHidden()
    assert window.enhance_button.isEnabled()


def test_show_error_updates_text(app):
    window = MainWindow()
    window.show_error("识别失败：onnxruntime is not installed")
    assert window.text_edit.toPlainText() == "识别失败：onnxruntime is not installed"
    assert "错误" in window.engine_label.text()
    assert not window.copy_button.isEnabled()


def test_copy_all_sets_clipboard(app):
    window = MainWindow()
    window.show_result("复制这段文字", "rapid")
    window.copy_all()
    assert QApplication.clipboard().text() == "复制这段文字"


def test_capture_button_emits_signal(app):
    window = MainWindow()
    received = []
    window.capture_requested.connect(lambda: received.append(True))
    window.capture_button.click()
    assert received == [True]


def test_capture_button_reenabled_after_busy_result(app):
    window = MainWindow()
    window.set_busy(True)
    assert not window.capture_button.isEnabled()
    window.show_result("完成", "baidu")
    assert window.capture_button.isEnabled()


def test_capture_buttons_are_icon_only_with_tooltips(app):
    window = MainWindow()
    assert window.capture_button.text() == ""
    assert window.shot_button.text() == ""
    assert not window.capture_button.icon().isNull()
    assert not window.shot_button.icon().isNull()
    assert "识别文字" in window.capture_button.toolTip()
    assert "截图" in window.shot_button.toolTip()


def test_shot_button_emits_signal(app):
    window = MainWindow()
    received = []
    window.shot_requested.connect(lambda: received.append(True))
    window.shot_button.click()
    assert received == [True]


def test_text_edit_is_editable(app):
    window = MainWindow()
    assert not window.text_edit.isReadOnly()


def test_restore_button_restores_original_text(app):
    window = MainWindow()
    window.show_result("原始文字", "rapid")
    window.text_edit.setPlainText("被我改过的文字")
    window.restore_button.click()
    assert window.text_edit.toPlainText() == "原始文字"


def test_copy_all_copies_edited_text(app):
    window = MainWindow()
    window.show_result("原始文字", "rapid")
    window.text_edit.setPlainText("修改后的文字")
    window.copy_all()
    assert QApplication.clipboard().text() == "修改后的文字"


def test_restore_button_disabled_on_error(app):
    window = MainWindow()
    window.show_error("识别失败")
    assert not window.restore_button.isEnabled()
