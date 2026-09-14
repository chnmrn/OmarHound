import numpy as np

from passport_filter.steps.degradation import photocopy_generations


def test_photocopy_generations_preserves_size(synthetic_face):
    result = photocopy_generations(synthetic_face, generations=2, jpeg_quality=40, scale_factor=0.5)

    assert result.mode == "L"
    assert result.size == synthetic_face.size


def test_photocopy_generations_softens_hard_edges(synthetic_face):
    result = photocopy_generations(synthetic_face, generations=2, jpeg_quality=40, scale_factor=0.5)
    array = np.asarray(result, dtype=np.int16)

    intermediate = (array > 10) & (array < 245)
    assert intermediate.any()
