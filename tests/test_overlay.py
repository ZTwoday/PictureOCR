from capture.screen import normalize_rect


def test_normalize_rect_drag_right_down():
    assert normalize_rect(10, 20, 60, 80) == (10, 20, 50, 60)


def test_normalize_rect_drag_backwards():
    assert normalize_rect(60, 80, 10, 20) == (10, 20, 50, 60)


def test_normalize_rect_zero_size():
    assert normalize_rect(10, 20, 10, 20) == (10, 20, 0, 0)
