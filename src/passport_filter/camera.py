from PIL import Image


def capture_frame() -> Image.Image:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "--camera requiere opencv-python (pip install passport-filter[camera])"
        ) from exc

    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    try:
        if not capture.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")
        ok, frame_bgr = capture.read()
        if not ok:
            raise RuntimeError("No se pudo capturar un frame de la cámara")
    finally:
        capture.release()

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb)
