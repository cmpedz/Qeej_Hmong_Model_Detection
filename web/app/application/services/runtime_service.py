from pathlib import Path
import uuid

from app.infrastructure.config.settings import OUTPUT_DIR, UPLOAD_DIR, clear_runtime_dirs
from app.shared.formatting import sanitize_filename

ALLOWED_AUDIO_EXTENSIONS = {".wav"}


def reset_runtime_state():
    clear_runtime_dirs()


def is_allowed_audio_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_AUDIO_EXTENSIONS


def save_uploaded_audio(audio_field):
    original_name = Path(audio_field["filename"]).name
    saved_name = f"{uuid.uuid4().hex[:8]}_{sanitize_filename(original_name)}"
    upload_path = UPLOAD_DIR / saved_name
    with upload_path.open("wb") as upload_file:
        upload_file.write(audio_field["bytes"])
    return upload_path


def resolve_output_media(relative_path):
    requested_path = (OUTPUT_DIR / relative_path).resolve()
    output_root = OUTPUT_DIR.resolve()
    if output_root not in requested_path.parents:
        raise PermissionError("Invalid file path.")
    if not requested_path.is_file():
        raise FileNotFoundError("File not found.")
    return requested_path
