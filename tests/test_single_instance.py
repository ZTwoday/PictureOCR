import main as main_module
from PySide6.QtNetwork import QLocalServer


def test_wake_returns_false_when_no_instance(app):
    assert main_module._wake_existing_instance("picture-ocr-test-absent") is False


def test_wake_returns_true_when_instance_listening(app):
    server = QLocalServer()
    server.removeServer("picture-ocr-test-active")
    assert server.listen("picture-ocr-test-active")
    try:
        assert main_module._wake_existing_instance("picture-ocr-test-active") is True
    finally:
        server.close()
