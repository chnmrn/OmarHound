from pathlib import Path

import numpy as np
from PIL import Image

from passport_filter.pipeline import run_pipeline
from passport_filter.steps.overlay import BlendMode

WINDOW_TITLE = "passport-filter (en vivo) - ESC para salir"


def run_live_preview(
    midpoint: float | None = None,
    pattern_path: Path | None = None,
    blend_mode: BlendMode = "multiply",
    opacity: float = 0.3,
    center_pattern_on_face: bool = False,
    process_width: int = 480,
    display_width: int = 900,
) -> None:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "--live requiere opencv-python (pip install passport-filter[camera])"
        ) from exc

    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not capture.isOpened():
        raise RuntimeError("No se pudo abrir la cámara")

    cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)
    window_sized = False

    try:
        while True:
            ok, frame_bgr = capture.read()
            if not ok:
                raise RuntimeError("No se pudo capturar un frame de la cámara")

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)

            if process_width and image.width > process_width:
                ratio = process_width / image.width
                image = image.resize((process_width, round(image.height * ratio)))

            result = run_pipeline(
                image,
                midpoint=midpoint,
                pattern_path=pattern_path,
                blend_mode=blend_mode,
                opacity=opacity,
                center_pattern_on_face=center_pattern_on_face,
            )
            result_bgr = cv2.cvtColor(np.array(result.convert("RGB")), cv2.COLOR_RGB2BGR)

            # la ventana es resizable (WINDOW_NORMAL) y OpenCV estira el frame
            # al tamaño de ventana actual, así que solo hace falta fijar un
            # tamaño inicial grande una vez, sin afectar la resolución de
            # procesamiento (más rápido) ni el aspect ratio real de la cámara
            if not window_sized:
                aspect_ratio = result_bgr.shape[0] / result_bgr.shape[1]
                cv2.resizeWindow(WINDOW_TITLE, display_width, round(display_width * aspect_ratio))
                window_sized = True

            cv2.imshow(WINDOW_TITLE, result_bgr)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()
