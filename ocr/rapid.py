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

    def _format_result(self, result: list) -> str:
        lines = []
        for item in result:
            try:
                _, text_info = item
                lines.append(text_info[0])
            except (IndexError, TypeError):
                continue
        return "\n".join(lines)

    def recognize(self, image_path: str) -> str:
        engine = self._ensure_engine()
        result, _ = engine(image_path)
        if not result:
            return ""
        return self._format_result(result)
