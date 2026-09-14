import numpy as np
from PIL import Image


def add_gaussian_noise(image: Image.Image, sigma: float = 12.0) -> Image.Image:
    array = np.asarray(image.convert("L"), dtype=np.float64)
    noise = np.random.normal(loc=0.0, scale=sigma, size=array.shape)
    noisy = np.clip(array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy, mode="L")
