from abc import ABC, abstractmethod


class OCRBackend(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def recognize(self, image_path: str) -> str:
        """识别图片中的文字，返回拼接后的纯文本。"""
