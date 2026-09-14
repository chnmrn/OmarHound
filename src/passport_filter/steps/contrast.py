import numpy as np
from PIL import Image

MIDPOINT_RANGE = (0.55, 0.8)


def apply_sigmoid_contrast(image: Image.Image, midpoint: float = 0.65, gain: float = 10.0) -> Image.Image:
    array = np.asarray(image.convert("L"), dtype=np.float64) / 255.0

    def sigmoid(x: float) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(gain * (midpoint - x)))

    low, high = sigmoid(0.0), sigmoid(1.0)
    normalized = (sigmoid(array) - low) / (high - low)

    output = np.clip(normalized * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(output, mode="L")


def auto_midpoint(image: Image.Image) -> float:
    histogram = image.convert("L").histogram()
    threshold = _otsu_threshold(histogram)
    midpoint = threshold / 255.0
    # Otsu separa fondo/rostro, pero fuera de este rango la curva deja de dar
    # el look "silueta casi negra + franja de luz" que define el estilo.
    return float(np.clip(midpoint, *MIDPOINT_RANGE))


def _otsu_threshold(histogram: list[int]) -> int:
    total = sum(histogram)
    sum_total = sum(i * count for i, count in enumerate(histogram))

    sum_background = 0.0
    weight_background = 0
    best_variance = -1.0
    best_threshold = 0

    for i, count in enumerate(histogram):
        weight_background += count
        if weight_background == 0:
            continue
        weight_foreground = total - weight_background
        if weight_foreground == 0:
            break

        sum_background += i * count
        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground

        variance_between = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
        if variance_between > best_variance:
            best_variance = variance_between
            best_threshold = i

    return best_threshold
