import base64
import threading

import webview
from werkzeug.serving import make_server

from passport_filter.gui.server import create_app

HOST = "127.0.0.1"
PORT = 5173


class ServerThread(threading.Thread):
    def __init__(self, flask_app):
        super().__init__(daemon=True)
        self.server = make_server(HOST, PORT, flask_app)

    def run(self) -> None:
        self.server.serve_forever()

    def shutdown(self) -> None:
        self.server.shutdown()


class Api:
    def save_image(self, data_url: str, filename: str) -> str | None:
        _, encoded = data_url.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        result = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename=filename)
        if not result:
            return None

        path = result if isinstance(result, str) else result[0]
        with open(path, "wb") as f:
            f.write(image_bytes)
        return path


def main() -> None:
    flask_app = create_app()
    server_thread = ServerThread(flask_app)
    server_thread.start()

    webview.create_window(
        "passport-filter",
        f"http://{HOST}:{PORT}",
        js_api=Api(),
        width=1150,
        height=820,
        min_size=(800, 600),
    )
    webview.start()
    server_thread.shutdown()


if __name__ == "__main__":
    main()
