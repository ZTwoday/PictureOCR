from PIL import Image

from scripts import generate_icon


def _ink(png_path):
    """Count dark-ink and light-ink pixels (alpha > 0)."""
    im = Image.open(png_path).convert("RGBA")
    dark = light = 0
    for x in range(im.width):
        for y in range(im.height):
            r, g, b, a = im.getpixel((x, y))
            if a > 0:
                if r < 128:
                    dark += 1
                else:
                    light += 1
    return dark, light


def test_generate_produces_expected_files(tmp_path, app):
    generate_icon.generate(str(tmp_path))
    assert (tmp_path / "app_icon.png").exists()
    assert (tmp_path / "tray_icon_16.png").exists()
    assert (tmp_path / "tray_icon_32.png").exists()
    assert (tmp_path / "app_icon.ico").exists()
    with Image.open(tmp_path / "app_icon.png") as im:
        assert im.size == (256, 256)
    with Image.open(tmp_path / "tray_icon_16.png") as im:
        assert im.size == (16, 16)
    with Image.open(tmp_path / "tray_icon_32.png") as im:
        assert im.size == (32, 32)
    with Image.open(tmp_path / "app_icon.ico") as im:
        assert im.size == (256, 256)


def test_app_icon_is_black_ink(tmp_path, app):
    generate_icon.generate(str(tmp_path))
    dark, light = _ink(str(tmp_path / "app_icon.png"))
    assert dark > 0


def test_tray_icon_is_white_ink(tmp_path, app):
    generate_icon.generate(str(tmp_path))
    dark, light = _ink(str(tmp_path / "tray_icon_32.png"))
    assert dark == 0
    assert light > 0
