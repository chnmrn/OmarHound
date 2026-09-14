from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def generate_crosshair_seal(size: int = 512) -> Image.Image:
    image = Image.new("L", (size, size), color=255)
    draw = ImageDraw.Draw(image)
    center = size // 2
    line_width = max(2, size // 60)

    draw.line([(center, size * 0.05), (center, size * 0.95)], fill=0, width=line_width)
    draw.line([(size * 0.05, center), (size * 0.95, center)], fill=0, width=line_width)

    for radius_ratio in (0.15, 0.30):
        radius = size * radius_ratio
        bbox = [center - radius, center - radius, center + radius, center + radius]
        draw.arc(bbox, start=200, end=340, fill=0, width=line_width)
        draw.arc(bbox, start=20, end=160, fill=0, width=line_width)

    return image


def generate_fingerprint_texture(size: int = 512, rings: int = 40) -> Image.Image:
    yy, xx = np.mgrid[0:size, 0:size]
    cx, cy = size * 0.5, size * 0.45
    dx, dy = xx - cx, yy - cy
    distance = np.sqrt(dx**2 + dy**2)
    angle = np.arctan2(dy, dx)

    warp = 8.0 * np.sin(angle * 3.0 + distance / 20.0)
    ridge = np.sin((distance + warp) / (size / (2 * rings)) * np.pi)

    pattern = np.where(ridge > 0.2, 0, 255).astype(np.uint8)
    return Image.fromarray(pattern, mode="L")


if __name__ == "__main__":
    patterns_dir = Path(__file__).resolve().parent.parent / "assets" / "patterns"
    generate_crosshair_seal().save(patterns_dir / "stamp_crosshair.png")
    generate_fingerprint_texture().save(patterns_dir / "stamp_fingerprint.png")
    print(f"Guardados en {patterns_dir}")
