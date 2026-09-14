from PIL import Image


def to_grayscale(image: Image.Image) -> Image.Image:
    return image.convert("L")
