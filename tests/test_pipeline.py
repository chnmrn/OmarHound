import numpy as np

from passport_filter.pipeline import run_pipeline


def test_run_pipeline_produces_grayscale_result(synthetic_face):
    np.random.seed(0)
    result = run_pipeline(synthetic_face)
    array = np.asarray(result)

    assert result.mode == "L"
    assert result.size == synthetic_face.size
    assert array[128, 128] > 200
