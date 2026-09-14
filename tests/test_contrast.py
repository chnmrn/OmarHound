import numpy as np

from passport_filter.steps.contrast import apply_sigmoid_contrast, auto_midpoint


def test_apply_sigmoid_contrast_darkens_low_values(synthetic_face):
    result = apply_sigmoid_contrast(synthetic_face, midpoint=0.65)
    array = np.asarray(result)

    assert result.size == synthetic_face.size
    assert result.mode == "L"
    assert array[0, 0] < 10
    assert array[128, 128] > 245


def test_auto_midpoint_returns_value_in_range(synthetic_face):
    midpoint = auto_midpoint(synthetic_face)
    assert 0.55 <= midpoint <= 0.8
