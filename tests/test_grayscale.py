from passport_filter.steps.grayscale import to_grayscale


def test_to_grayscale_converts_mode(synthetic_face):
    result = to_grayscale(synthetic_face)

    assert result.mode == "L"
    assert result.size == synthetic_face.size
