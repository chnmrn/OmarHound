import numpy as np
from PIL import Image

Box = tuple[int, int, int, int]


def detect_face_box(image: Image.Image) -> Box | None:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "detectar caras requiere opencv-python (pip install passport-filter[camera])"
        ) from exc

    gray = np.array(image.convert("L"))
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    classifier = cv2.CascadeClassifier(cascade_path)
    faces = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(faces) == 0:
        return None

    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    return int(x), int(y), int(w), int(h)


def expand_box(box: Box, image_size: tuple[int, int], margin: float = 0.4) -> Box:
    x, y, w, h = box
    width, height = image_size

    new_w = min(w * (1 + margin), width)
    new_h = min(h * (1 + margin), height)
    new_x = min(max(0.0, x - (new_w - w) / 2), width - new_w)
    new_y = min(max(0.0, y - (new_h - h) / 2), height - new_h)

    return int(new_x), int(new_y), int(new_w), int(new_h)
