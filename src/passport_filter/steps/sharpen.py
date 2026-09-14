from PIL import Image, ImageFilter


def blur_unsharp(image: Image.Image, blur_radius: float = 1.5, unsharp_amount: float = 2.0) -> Image.Image:
    grayscale = image.convert("L")
    blurred = grayscale.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    percent = round(unsharp_amount * 100)
    return blurred.filter(ImageFilter.UnsharpMask(radius=blur_radius, percent=percent, threshold=0))
