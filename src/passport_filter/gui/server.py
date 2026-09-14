import base64
import io
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from PIL import Image

from passport_filter.assets_dir import PATTERNS_DIR
from passport_filter.pipeline import run_pipeline

USER_PATTERNS_DIR = Path.home() / ".passport_filter" / "patterns"
PATTERN_EXTENSIONS = ("*.png", "*.jpg", "*.jpeg")


def _list_pattern_files(directory: Path) -> list[Path]:
    return sorted(p for ext in PATTERN_EXTENSIONS for p in directory.glob(ext))


def create_app() -> Flask:
    USER_PATTERNS_DIR.mkdir(parents=True, exist_ok=True)
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/patterns")
    def list_patterns():
        builtin = [{"name": p.stem, "path": str(p), "source": "builtin"} for p in _list_pattern_files(PATTERNS_DIR)]
        custom = [{"name": p.stem, "path": str(p), "source": "custom"} for p in _list_pattern_files(USER_PATTERNS_DIR)]
        return jsonify(builtin + custom)

    @app.get("/api/patterns/thumbnail")
    def pattern_thumbnail():
        path = Path(request.args["path"]).resolve()
        if PATTERNS_DIR not in path.parents and USER_PATTERNS_DIR not in path.parents:
            return "not found", 404
        return send_file(path)

    @app.post("/api/patterns/upload")
    def upload_pattern():
        file = request.files["file"]
        destination = USER_PATTERNS_DIR / Path(file.filename).name
        file.save(destination)
        return jsonify({"name": destination.stem, "path": str(destination), "source": "custom"})

    @app.delete("/api/patterns")
    def delete_pattern():
        path = Path(request.args["path"]).resolve()
        if USER_PATTERNS_DIR not in path.parents:
            return jsonify({"error": "Only your own patterns can be deleted, not the built-in ones"}), 400
        if not path.exists():
            return jsonify({"error": "That pattern no longer exists"}), 404

        path.unlink()
        return jsonify({"ok": True})

    @app.post("/api/camera/capture")
    def camera_capture():
        from passport_filter.camera import capture_frame

        try:
            image = capture_frame()
        except RuntimeError:
            return jsonify({"error": "Could not access the camera"}), 400

        return jsonify({"image": _image_to_data_url(image)})

    @app.post("/api/process")
    def process():
        photo_data_url = request.form.get("photo_data_url")
        if photo_data_url:
            image = _data_url_to_image(photo_data_url)
        elif "photo" in request.files:
            image = Image.open(request.files["photo"].stream)
        else:
            return jsonify({"error": "No photo was received"}), 400

        pattern_path = request.form.get("pattern_path") or None
        blend_mode = request.form.get("blend_mode", "multiply")
        opacity = float(request.form.get("opacity", 0.3))
        midpoint = request.form.get("midpoint") or None
        center_on_face = request.form.get("center_on_face") == "true"

        face_message = None
        if pattern_path is not None and center_on_face:
            from passport_filter.steps.face import detect_face_box

            if detect_face_box(image) is not None:
                face_message = "Face detected: the pattern was centered on it."
            else:
                face_message = "No face was detected; the pattern was applied over the whole photo."

        result = run_pipeline(
            image,
            midpoint=float(midpoint) if midpoint else None,
            pattern_path=Path(pattern_path) if pattern_path else None,
            blend_mode=blend_mode,
            opacity=opacity,
            center_pattern_on_face=center_on_face,
        )

        return jsonify({"image": _image_to_data_url(result), "face_message": face_message})

    return app


def _image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=90)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _data_url_to_image(data_url: str) -> Image.Image:
    _, encoded = data_url.split(",", 1)
    return Image.open(io.BytesIO(base64.b64decode(encoded)))
