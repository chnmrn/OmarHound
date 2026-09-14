from pathlib import Path
from typing import Literal

import numpy as np
from PIL import Image

from passport_filter.steps.face import Box

BlendMode = Literal["screen", "multiply", "overlay"]

_BLEND_IDENTITY: dict[BlendMode, float] = {"multiply": 1.0, "screen": 0.0, "overlay": 0.5}


def overlay_pattern(
    image: Image.Image,
    pattern_path: Path,
    mode: BlendMode = "multiply",
    opacity: float = 0.3,
    region: Box | None = None,
) -> Image.Image:
    if mode not in _BLEND_IDENTITY:
        raise ValueError(f"Blend mode desconocido: {mode}")

    base = np.asarray(image.convert("L"), dtype=np.float64) / 255.0
    pattern_image = Image.open(pattern_path).convert("L")

    if region is None:
        pattern_image = pattern_image.resize(image.size)
    else:
        x, y, w, h = region
        pattern_image = pattern_image.resize((w, h))
        canvas = Image.new("L", image.size, color=round(_BLEND_IDENTITY[mode] * 255))
        canvas.paste(pattern_image, (x, y))
        pattern_image = canvas

    pattern = np.asarray(pattern_image, dtype=np.float64) / 255.0

    if mode == "multiply":
        blended = base * pattern
    elif mode == "screen":
        blended = 1.0 - (1.0 - base) * (1.0 - pattern)
    else:
        blended = np.where(
            base < 0.5,
            2.0 * base * pattern,
            1.0 - 2.0 * (1.0 - base) * (1.0 - pattern),
        )

    result = base * (1.0 - opacity) + blended * opacity
    output = np.clip(result * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(output, mode="L")
