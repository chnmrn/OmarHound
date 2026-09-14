from pathlib import Path

from PIL import Image

from passport_filter.steps import grayscale
from passport_filter.steps.contrast import apply_sigmoid_contrast, auto_midpoint
from passport_filter.steps.degradation import photocopy_generations
from passport_filter.steps.dithering import ordered_dither
from passport_filter.steps.noise import add_gaussian_noise
from passport_filter.steps.overlay import overlay_pattern
from passport_filter.steps.sharpen import blur_unsharp


def run_pipeline(
    image: Image.Image,
    midpoint: float | None = None,
    pattern_path: Path | None = None,
) -> Image.Image:
    gray = grayscale.to_grayscale(image)
    effective_midpoint = midpoint if midpoint is not None else auto_midpoint(gray)
    contrasted = apply_sigmoid_contrast(gray, midpoint=effective_midpoint)
    dithered = ordered_dither(contrasted)
    overlaid = overlay_pattern(dithered, pattern_path) if pattern_path is not None else dithered
    noisy = add_gaussian_noise(overlaid)
    degraded = photocopy_generations(noisy)
    return blur_unsharp(degraded)
