from ocr.base import OCRBackend

try:
    from rapidocr import RapidOCR
except ImportError:
    from rapidocr_onnxruntime import RapidOCR


class RapidOCRBackend(OCRBackend):
    _name = "rapid"

    def __init__(self):
        self._engine = None

    @property
    def name(self) -> str:
        return self._name

    def _ensure_engine(self):
        if self._engine is None:
            self._engine = RapidOCR()
        return self._engine

    def recognize(self, image_path: str) -> str:
        engine = self._ensure_engine()
        out = engine(image_path)
        return "\n".join(t for t in out.txts if t)
