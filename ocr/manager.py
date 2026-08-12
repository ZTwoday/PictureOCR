from PySide6.QtCore import QObject, QThread, Signal

from core.config import load_config
from ocr.baidu import BaiduOCRBackend
from ocr.rapid import RapidOCRBackend
from security.creds import get_baidu_creds

FALLBACK_ORDER = ["baidu", "rapid"]


def make_backend(engine: str):
    if engine == "rapid":
        return RapidOCRBackend()
    if engine == "baidu":
        creds = get_baidu_creds()
        if creds is None:
            raise RuntimeError("百度 OCR 未配置 API Key，请在设置中填写")
        return BaiduOCRBackend(*creds)
    raise ValueError(f"unknown engine: {engine}")


class _Worker(QObject):
    done = Signal(str, str)
    failed = Signal(str)

    def __init__(self, image_path: str, engine: str, backends: dict):
        super().__init__()
        self.image_path = image_path
        self.engine = engine
        self.backends = backends

    def run(self):
        text, engine = self._run(self.engine)
        if text is not None:
            self.done.emit(text, engine)
        else:
            reason = engine if engine != "no backend" else "无可用识别引擎"
            self.failed.emit(f"识别失败：{reason}")

    def _run(self, requested: str):
        order = [requested] + [e for e in FALLBACK_ORDER if e != requested]
        last_error = None
        for name in order:
            backend = self.backends.get(name)
            if backend is None:
                continue
            try:
                return backend.recognize(self.image_path), name
            except Exception as e:  # noqa: BLE001
                last_error = e
        return None, (last_error and str(last_error)) or "no backend"


class OCRManager(QObject):
    finished = Signal(str, str)
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._threads = []
        self._workers = []
        self._backends = {}

    def get_available_engines(self) -> list[str]:
        return ["rapid", "baidu"]

    def _load_backends(self, engine: str) -> dict:
        backends = {}
        try:
            backends[engine] = make_backend(engine)
        except (RuntimeError, ValueError):
            pass
        for alt in FALLBACK_ORDER:
            if alt not in backends:
                try:
                    backends[alt] = make_backend(alt)
                except (RuntimeError, ValueError):
                    pass
        return backends

    def _make_worker(self, image_path: str, engine: str, backends: dict) -> _Worker:
        worker = _Worker(image_path, engine, backends)
        worker.done.connect(lambda text, eng: self.finished.emit(text, eng))
        worker.failed.connect(lambda msg: self.error.emit(msg))
        return worker

    def _run_recognize(self, image_path: str, engine: str, backends: dict):
        self._make_worker(image_path, engine, backends).run()

    def recognize_async(self, image_path: str, engine: str | None = None) -> None:
        engine = engine or load_config().get("default_engine", "rapid")
        backends = self._load_backends(engine)
        worker = self._make_worker(image_path, engine, backends)
        thread = QThread(self)
        self._threads.append(thread)
        self._workers.append(worker)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.done.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.done.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        def _cleanup():
            self._threads.remove(thread)
            self._workers.remove(worker)

        thread.finished.connect(_cleanup)
        thread.start()
