from urllib.parse import quote

from app.infrastructure.config.settings import OUTPUT_DIR


def build_media_url(file_path):
    relative_path = file_path.resolve().relative_to(OUTPUT_DIR.resolve())
    return f"/media?file={quote(relative_path.as_posix())}"


def build_download_url(file_path, download_name=""):
    relative_path = file_path.resolve().relative_to(OUTPUT_DIR.resolve())
    download_url = f"/media?file={quote(relative_path.as_posix())}&download=1"
    if download_name:
        download_url += f"&name={quote(download_name)}"
    return download_url
