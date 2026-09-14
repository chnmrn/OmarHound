import numpy as np

from passport_filter.steps.noise import add_gaussian_noise


def test_add_gaussian_noise_preserves_size_and_mode(synthetic_face):
    np.random.seed(0)
    result = add_gaussian_noise(synthetic_face, sigma=12.0)

    assert result.mode == "L"
    assert result.size == synthetic_face.size


def test_add_gaussian_noise_changes_pixel_values(synthetic_face):
    np.random.seed(0)
    result = add_gaussian_noise(synthetic_face, sigma=12.0)
    original = np.asarray(synthetic_face.convert("L"), dtype=np.int16)
    noisy = np.asarray(result, dtype=np.int16)

    assert not np.array_equal(original, noisy)
