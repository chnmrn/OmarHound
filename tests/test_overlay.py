from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from passport_filter.steps.overlay import overlay_pattern


@pytest.fixture
def checkerboard_pattern(tmp_path: Path) -> Path:
    array = (np.indices((64, 64)).sum(axis=0) % 2 * 255).astype(np.uint8)
    pattern = Image.fromarray(array, mode="L")
    path = tmp_path / "pattern.png"
    pattern.save(path)
    return path


def test_overlay_pattern_preserves_size_and_mode(synthetic_face, checkerboard_pattern):
    result = overlay_pattern(synthetic_face, checkerboard_pattern, mode="multiply", opacity=0.5)

    assert result.mode == "L"
    assert result.size == synthetic_face.size


def test_overlay_pattern_multiply_darkens_image(synthetic_face, checkerboard_pattern):
    result = overlay_pattern(synthetic_face, checkerboard_pattern, mode="multiply", opacity=1.0)
    original = np.asarray(synthetic_face.convert("L"), dtype=np.int16)
    blended = np.asarray(result, dtype=np.int16)

    assert blended.mean() <= original.mean()


def test_overlay_pattern_rejects_unknown_mode(synthetic_face, checkerboard_pattern):
    with pytest.raises(ValueError):
        overlay_pattern(synthetic_face, checkerboard_pattern, mode="invalid", opacity=0.5)
