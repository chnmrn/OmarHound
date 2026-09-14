import numpy as np
from PIL import Image

BAYER_4X4 = np.array(
    [
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5],
    ]
) / 16.0


def ordered_dither(image: Image.Image) -> Image.Image:
    array = np.asarray(image.convert("L"), dtype=np.float64) / 255.0
    height, width = array.shape

    tiles_y = -(-height // 4)
    tiles_x = -(-width // 4)
    threshold = np.tile(BAYER_4X4, (tiles_y, tiles_x))[:height, :width]

    dithered = np.where(array > threshold, 255, 0).astype(np.uint8)
    return Image.fromarray(dithered, mode="L")
