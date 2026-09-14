import io

from PIL import Image


def photocopy_generations(
    image: Image.Image,
    generations: int = 3,
    jpeg_quality: int = 40,
    scale_factor: float = 0.5,
) -> Image.Image:
    original_size = image.size
    small_size = (
        max(1, round(original_size[0] * scale_factor)),
        max(1, round(original_size[1] * scale_factor)),
    )

    current = image.convert("L")
    for _ in range(generations):
        downscaled = current.resize(small_size, Image.BILINEAR)
        upscaled = downscaled.resize(original_size, Image.BILINEAR)

        buffer = io.BytesIO()
        upscaled.save(buffer, format="JPEG", quality=jpeg_quality)
        buffer.seek(0)
        current = Image.open(buffer).convert("L")

    return current
