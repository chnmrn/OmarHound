import numpy as np

from passport_filter.steps.sharpen import blur_unsharp


def test_blur_unsharp_preserves_size_and_mode(synthetic_face):
    result = blur_unsharp(synthetic_face, blur_radius=1.5, unsharp_amount=2.0)

    assert result.mode == "L"
    assert result.size == synthetic_face.size


def test_blur_unsharp_changes_pixel_values(synthetic_face):
    result = blur_unsharp(synthetic_face, blur_radius=1.5, unsharp_amount=2.0)
    original = np.asarray(synthetic_face.convert("L"), dtype=np.int16)
    processed = np.asarray(result, dtype=np.int16)

    assert not np.array_equal(original, processed)
