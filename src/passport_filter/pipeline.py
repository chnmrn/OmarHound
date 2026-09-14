from pathlib import Path

from PIL import Image

from passport_filter.steps import grayscale
from passport_filter.steps.contrast import apply_sigmoid_contrast, auto_midpoint
from passport_filter.steps.degradation import photocopy_generations
from passport_filter.steps.dithering import ordered_dither
from passport_filter.steps.face import detect_face_box, expand_box
from passport_filter.steps.noise import add_gaussian_noise
from passport_filter.steps.overlay import BlendMode, overlay_pattern
from passport_filter.steps.sharpen import blur_unsharp


def run_pipeline(
    image: Image.Image,
    midpoint: float | None = None,
    pattern_path: Path | None = None,
    blend_mode: BlendMode = "multiply",
    opacity: float = 0.3,
    center_pattern_on_face: bool = False,
) -> Image.Image:
    gray = grayscale.to_grayscale(image)
    effective_midpoint = midpoint if midpoint is not None else auto_midpoint(gray)
    contrasted = apply_sigmoid_contrast(gray, midpoint=effective_midpoint)
    dithered = ordered_dither(contrasted)

    region = None
    if pattern_path is not None and center_pattern_on_face:
        face_box = detect_face_box(image)
        if face_box is not None:
            region = expand_box(face_box, image.size)

    overlaid = (
        overlay_pattern(dithered, pattern_path, mode=blend_mode, opacity=opacity, region=region)
        if pattern_path is not None
        else dithered
    )
    noisy = add_gaussian_noise(overlaid)
    degraded = photocopy_generations(noisy)
    return blur_unsharp(degraded)
