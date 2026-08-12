from ocr.rapid import RapidOCRBackend


def _patch_engine(monkeypatch, txts):
    class FakeOutput:
        def __init__(self, txts):
            self.txts = txts

    class FakeEngine:
        def __call__(self, image_path):
            return FakeOutput(txts)

    backend = RapidOCRBackend()
    monkeypatch.setattr(backend, "_ensure_engine", lambda: FakeEngine())
    return backend


def test_recognize_joins_lines(monkeypatch):
    backend = _patch_engine(monkeypatch, ["你好世界", "second line"])
    assert backend.recognize("whatever.png") == "你好世界\nsecond line"


def test_recognize_handles_empty(monkeypatch):
    backend = _patch_engine(monkeypatch, [])
    assert backend.recognize("whatever.png") == ""


def test_recognize_filters_blank_lines(monkeypatch):
    backend = _patch_engine(monkeypatch, ["hello", "", "world"])
    assert backend.recognize("whatever.png") == "hello\nworld"
