from pathlib import Path
from typing import Literal

import numpy as np
from PIL import Image

BlendMode = Literal["screen", "multiply", "overlay"]


def overlay_pattern(
    image: Image.Image,
    pattern_path: Path,
    mode: BlendMode = "multiply",
    opacity: float = 0.3,
) -> Image.Image:
    base = np.asarray(image.convert("L"), dtype=np.float64) / 255.0

    pattern_image = Image.open(pattern_path).convert("L").resize(image.size)
    pattern = np.asarray(pattern_image, dtype=np.float64) / 255.0

    if mode == "multiply":
        blended = base * pattern
    elif mode == "screen":
        blended = 1.0 - (1.0 - base) * (1.0 - pattern)
    elif mode == "overlay":
        blended = np.where(
            base < 0.5,
            2.0 * base * pattern,
            1.0 - 2.0 * (1.0 - base) * (1.0 - pattern),
        )
    else:
        raise ValueError(f"Blend mode desconocido: {mode}")

    result = base * (1.0 - opacity) + blended * opacity
    output = np.clip(result * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(output, mode="L")
