import numpy as np

from passport_filter.steps.dithering import ordered_dither


def test_ordered_dither_preserves_size(synthetic_face):
    result = ordered_dither(synthetic_face)

    assert result.mode == "L"
    assert result.size == synthetic_face.size


def test_ordered_dither_output_is_binary(synthetic_face):
    result = ordered_dither(synthetic_face)
    array = np.asarray(result)

    assert set(np.unique(array)).issubset({0, 255})
