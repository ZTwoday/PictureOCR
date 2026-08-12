from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from ui.result_popup import ResultPopup


def test_popup_shows_text_and_engine(app):
    popup = ResultPopup()
    popup.show_result("测试文字", "rapid", on_enhance=None)
    assert "测试文字" in popup.text_edit.toPlainText()
    assert "rapid" in popup.engine_label.text()


def test_copy_all_writes_clipboard(app):
    from PySide6.QtWidgets import QApplication
    popup = ResultPopup()
    popup.show_result("hello", "rapid", on_enhance=None)
    popup.copy_all()
    assert QApplication.clipboard().text() == "hello"


def test_note_label_shows_and_hides(app):
    popup = ResultPopup()
    popup.show_result("hi", "rapid", on_enhance=None, note="百度不可用")
    assert popup.note_label.text() == "百度不可用"
    assert not popup.note_label.isHidden()
    popup.show_result("hi", "rapid", on_enhance=None)
    assert popup.note_label.isHidden()
