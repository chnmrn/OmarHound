import base64
import io
from urllib.parse import quote

import numpy as np
from PIL import Image

from passport_filter.assets_dir import PATTERNS_DIR
from passport_filter.gui.server import create_app


def _client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_list_patterns_includes_builtin_assets():
    client = _client()
    response = client.get("/api/patterns")

    assert response.status_code == 200
    names = {pattern["name"] for pattern in response.get_json()}
    assert "guilloche" in names
    assert "stamp_crosshair" in names


def test_process_without_photo_returns_error():
    client = _client()
    response = client.post("/api/process", data={})

    assert response.status_code == 400


def test_process_with_uploaded_photo_returns_image(synthetic_face):
    client = _client()
    buffer = io.BytesIO()
    synthetic_face.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/api/process",
        data={"photo": (buffer, "face.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["image"].startswith("data:image/jpeg;base64,")


def test_process_with_large_photo_data_url_returns_image():
    # The frontend always sends photo_data_url as a form field; Flask caps those
    # at 500 KB by default, which made any real photo fail with a 413.
    client = _client()
    noise = np.random.default_rng(0).integers(0, 256, (1200, 1600, 3), dtype=np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(noise).save(buffer, format="JPEG", quality=90)
    data_url = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    assert len(data_url) > 1_000_000

    response = client.post("/api/process", data={"photo_data_url": data_url})

    assert response.status_code == 200
    assert response.get_json()["image"].startswith("data:image/jpeg;base64,")


def test_process_rejects_unknown_blend_mode(synthetic_face):
    client = _client()
    buffer = io.BytesIO()
    synthetic_face.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/api/process",
        data={"photo": (buffer, "face.png"), "blend_mode": "does-not-exist"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "does-not-exist" in response.get_json()["error"]


def test_upload_pattern_without_filename_returns_error(synthetic_face):
    client = _client()
    buffer = io.BytesIO()
    synthetic_face.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/api/patterns/upload",
        data={"file": (buffer, "")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_upload_then_delete_pattern_round_trip(synthetic_face):
    client = _client()
    buffer = io.BytesIO()
    synthetic_face.save(buffer, format="PNG")
    buffer.seek(0)

    upload_response = client.post(
        "/api/patterns/upload",
        data={"file": (buffer, "test_custom_pattern.png")},
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 200
    uploaded = upload_response.get_json()
    assert uploaded["source"] == "custom"
    assert "test_custom_pattern" in {p["name"] for p in client.get("/api/patterns").get_json()}

    delete_response = client.delete(f"/api/patterns?path={quote(uploaded['path'])}")
    assert delete_response.status_code == 200
    assert "test_custom_pattern" not in {p["name"] for p in client.get("/api/patterns").get_json()}


def test_delete_pattern_rejects_builtin_assets():
    client = _client()
    builtin_path = str(PATTERNS_DIR / "guilloche.png")

    response = client.delete(f"/api/patterns?path={quote(builtin_path)}")

    assert response.status_code == 400
    assert (PATTERNS_DIR / "guilloche.png").exists()


def test_upload_jpeg_pattern_appears_in_listing_and_thumbnail(synthetic_face):
    client = _client()
    buffer = io.BytesIO()
    synthetic_face.save(buffer, format="JPEG")
    buffer.seek(0)

    upload_response = client.post(
        "/api/patterns/upload",
        data={"file": (buffer, "test_custom_pattern_jpg.jpg")},
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 200
    uploaded = upload_response.get_json()

    listing = client.get("/api/patterns").get_json()
    assert "test_custom_pattern_jpg" in {p["name"] for p in listing}

    thumbnail_response = client.get(f"/api/patterns/thumbnail?path={quote(uploaded['path'])}")
    assert thumbnail_response.status_code == 200
    thumbnail_response.close()

    client.delete(f"/api/patterns?path={quote(uploaded['path'])}")
