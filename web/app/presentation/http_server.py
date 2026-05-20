from pathlib import Path
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import perf_counter
from urllib.parse import parse_qs, quote, urlparse

from app.application.services.prediction_service import run_inference
from app.application.services.runtime_service import (
    is_allowed_audio_file,
    reset_runtime_state,
    resolve_output_media,
    save_uploaded_audio,
)
from app.infrastructure.config.settings import HOST, MODEL_PATH, PORT, ensure_runtime_dirs
from app.presentation.parsers.multipart import parse_multipart_form_data
from app.presentation.views.page_view import render_page
from app.shared.formatting import sanitize_filename


class MKQHRequestHandler(BaseHTTPRequestHandler):
    server_version = "MKQHGuide/1.0"

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/":
            self.send_html(render_page())
            return

        if parsed_url.path == "/media":
            self.handle_media(parsed_url)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Không tìm thấy trang")

    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path != "/predict":
            self.send_error(HTTPStatus.NOT_FOUND, "Không tìm thấy trang")
            return
        self.handle_predict()

    def handle_predict(self):
        request_started_at = perf_counter()
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self.send_html(render_page(error_message="Dữ liệu gửi đi cần phải là multipart/form-data"), status=HTTPStatus.BAD_REQUEST)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        request_body = self.rfile.read(content_length)
        form = parse_multipart_form_data(content_type, request_body)

        if "audio" not in form:
            self.send_html(render_page(error_message="Bạn cần tải lên một tệp âm thanh"), status=HTTPStatus.BAD_REQUEST)
            return

        audio_field = form["audio"]
        if not audio_field.get("filename"):
            self.send_html(render_page(error_message="Không thể đọc tệp âm thanh đã tải lên"), status=HTTPStatus.BAD_REQUEST)
            return
        if not is_allowed_audio_file(audio_field["filename"]):
            self.send_html(render_page(error_message="Hệ thống chỉ hỗ trợ tệp âm thanh định dạng .wav"), status=HTTPStatus.BAD_REQUEST)
            return

        reset_runtime_state()
        upload_path = save_uploaded_audio(audio_field)

        try:
            result = run_inference(upload_path)
        except Exception as exc:
            self.send_html(render_page(error_message=str(exc)), status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        result.timings_ms["request_total"] = (perf_counter() - request_started_at) * 1000
        self.send_html(render_page(result=result), status=HTTPStatus.OK)

    def handle_media(self, parsed_url):
        query = parse_qs(parsed_url.query)
        relative_path = query.get("file", [None])[0]
        download_requested = query.get("download", ["0"])[0] == "1"
        if not relative_path:
            self.send_error(HTTPStatus.BAD_REQUEST, "Thiếu tham số file")
            return

        try:
            requested_path = resolve_output_media(relative_path)
        except PermissionError as exc:
            self.send_error(HTTPStatus.FORBIDDEN, "Bạn không có quyền truy cập tệp này")
            return
        except FileNotFoundError as exc:
            self.send_error(HTTPStatus.NOT_FOUND, "Tệp không tồn tại")
            return

        suffix = requested_path.suffix.lower()
        if suffix == ".gif":
            content_type = "image/gif"
        elif suffix == ".png":
            content_type = "image/png"
        elif suffix == ".pdf":
            content_type = "application/pdf"
        elif suffix == ".mp4":
            content_type = "video/mp4"
        elif suffix == ".webm":
            content_type = "video/webm"
        else:
            content_type = "application/octet-stream"

        payload = requested_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        if download_requested:
            requested_name = query.get("name", [requested_path.name])[0]
            download_name = Path(requested_name).name or requested_path.name
            fallback_name = sanitize_filename(download_name) or requested_path.name
            encoded_name = quote(download_name)
            self.send_header(
                "Content-Disposition",
                f"attachment; filename=\"{fallback_name}\"; filename*=UTF-8''{encoded_name}",
            )
        self.end_headers()
        self.wfile.write(payload)

    def send_html(self, body, status=HTTPStatus.OK):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format_string, *args):
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format_string % args}")


def serve(host=HOST, port=PORT):
    ensure_runtime_dirs()
    server = ThreadingHTTPServer((host, port), MKQHRequestHandler)
    print(f"MKQH web is running at http://{host}:{port}")
    print(f"Using model: {MODEL_PATH}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()
