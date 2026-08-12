import pytest

from ocr.manager import OCRManager, make_backend


class FakeBackend:
    name = "fake"

    def __init__(self, text="fake text"):
        self._text = text

    def recognize(self, image_path):
        if self._text == "boom":
            raise RuntimeError("boom")
        return self._text


def test_make_backend_rapid():
    from ocr.rapid import RapidOCRBackend
    assert isinstance(make_backend("rapid"), RapidOCRBackend)


def test_make_backend_unknown_raises():
    with pytest.raises(ValueError):
        make_backend("nope")


def test_recognize_success(monkeypatch):
    from ocr import manager as m
    engines = {"rapid": FakeBackend("ok text")}
    monkeypatch.setattr(m, "make_backend", lambda name: engines[name])
    mgr = OCRManager()
    results = []
    mgr.finished.connect(lambda text, engine: results.append((text, engine)))
    mgr._run_recognize("x.png", "rapid", engines)
    assert results == [("ok text", "rapid")]


def test_fallback_from_baidu_to_rapid(monkeypatch):
    from ocr import manager as m
    engines = {"rapid": FakeBackend("fallback text"), "baidu": FakeBackend("boom")}
    monkeypatch.setattr(m, "make_backend", lambda name: engines[name])
    mgr = OCRManager()
    results = []
    mgr.finished.connect(lambda text, engine: results.append((text, engine)))
    mgr._run_recognize("x.png", "baidu", engines)
    assert results and results[0] == ("fallback text", "rapid")


def test_all_backends_fail_emits_reason(monkeypatch):
    from ocr import manager as m
    engines = {"rapid": FakeBackend("boom")}
    monkeypatch.setattr(m, "make_backend", lambda name: engines[name])
    mgr = OCRManager()
    errors = []
    mgr.error.connect(lambda msg: errors.append(msg))
    mgr._run_recognize("x.png", "rapid", engines)
    assert errors and "boom" in errors[0]
