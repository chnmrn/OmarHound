import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def synthetic_face() -> Image.Image:
    array = np.zeros((256, 256, 3), dtype=np.uint8)
    array[96:160, 96:160] = 255
    return Image.fromarray(array)
