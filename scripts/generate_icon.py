"""Generate app icon assets (PNG/ICO) from assets/icons/app_icon.svg.

Rasterize the SVG at each size with Qt's SVG renderer. The tray icon is the
same drawing with its ink recolored to white so it stays visible on a dark
Windows taskbar.

Usage: .venv/Scripts/python scripts/generate_icon.py
"""
import os

from PIL import Image
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SVG = os.path.join(REPO_ROOT, "assets", "icons", "app_icon.svg")
APP_SIZES = [16, 32, 48, 64, 128, 256]


def render_svg(svg_path, size):
    renderer = QSvgRenderer(svg_path)
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    painter = QPainter(img)
    renderer.render(painter, QRect(0, 0, size, size))
    painter.end()
    return img


def _to_pil(img):
    rgba = img.convertToFormat(QImage.Format_RGBA8888)
    return Image.frombytes("RGBA", (rgba.width(), rgba.height()), bytes(rgba.constBits()))


def _white_ink(img):
    out = img.convertToFormat(QImage.Format_ARGB32)
    for y in range(out.height()):
        for x in range(out.width()):
            color = out.pixelColor(x, y)
            if color.alpha() > 0:
                out.setPixelColor(x, y, QColor(255, 255, 255, color.alpha()))
    return out


def generate(output_dir, svg_path=DEFAULT_SVG):
    os.makedirs(output_dir, exist_ok=True)

    _to_pil(render_svg(svg_path, 256)).save(os.path.join(output_dir, "app_icon.png"))

    tray16 = _white_ink(render_svg(svg_path, 16))
    tray32 = _white_ink(render_svg(svg_path, 32))
    _to_pil(tray16).save(os.path.join(output_dir, "tray_icon_16.png"))
    _to_pil(tray32).save(os.path.join(output_dir, "tray_icon_32.png"))

    images = [_to_pil(render_svg(svg_path, s)) for s in APP_SIZES]
    ico_path = os.path.join(output_dir, "app_icon.ico")
    images[-1].save(ico_path, format="ICO",
                    sizes=[(s, s) for s in APP_SIZES], append_images=images[:-1])

    white_256 = _white_ink(render_svg(svg_path, 256))
    _to_pil(white_256).save(os.path.join(output_dir, "app_icon_white.png"))
    white_images = [_to_pil(_white_ink(render_svg(svg_path, s))) for s in APP_SIZES]
    white_ico_path = os.path.join(output_dir, "app_icon_white.ico")
    white_images[-1].save(white_ico_path, format="ICO",
                          sizes=[(s, s) for s in APP_SIZES], append_images=white_images[:-1])
    return ico_path


if __name__ == "__main__":
    out_dir = os.path.join(REPO_ROOT, "assets", "icons")
    path = generate(out_dir)
    print(f"wrote {path}")
