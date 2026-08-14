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
