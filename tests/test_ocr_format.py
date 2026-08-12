from ocr.rapid import RapidOCRBackend


def test_format_result_joins_lines():
    backend = RapidOCRBackend()
    result = [
        [[[10, 10], [100, 10], [100, 30], [10, 30]], ("你好世界", 0.99)],
        [[[10, 40], [200, 40], [200, 60], [10, 60]], ("second line", 0.98)],
    ]
    assert backend._format_result(result) == "你好世界\nsecond line"


def test_format_result_handles_empty():
    assert RapidOCRBackend()._format_result([]) == ""
