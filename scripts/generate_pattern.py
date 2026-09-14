from pathlib import Path

import numpy as np
from PIL import Image


def generate_guilloche_pattern(size: tuple[int, int] = (512, 512)) -> Image.Image:
    width, height = size
    yy, xx = np.mgrid[0:height, 0:width]

    wave1 = np.sin(xx / 9.0 + yy / 25.0)
    wave2 = np.sin(xx / 14.0 - yy / 11.0)
    wave3 = np.sin((xx + yy) / 17.0)

    pattern = (wave1 + wave2 + wave3) / 3.0
    normalized = ((pattern + 1.0) / 2.0 * 255.0).astype(np.uint8)
    return Image.fromarray(normalized, mode="L")


if __name__ == "__main__":
    output_path = Path(__file__).resolve().parent.parent / "assets" / "patterns" / "guilloche.png"
    generate_guilloche_pattern().save(output_path)
    print(f"Guardado en {output_path}")
