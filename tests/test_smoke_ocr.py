import pytest
from PIL import Image, ImageDraw
from ocr.rapid import RapidOCRBackend


@pytest.mark.smoke
def test_rapid_recognizes_generated_image(tmp_path):
    img = Image.new("RGB", (400, 100), "white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 30), "HELLO OCR", fill="black")
    path = tmp_path / "sample.png"
    img.save(path)
    text = RapidOCRBackend().recognize(str(path))
    assert "HELLO" in text
