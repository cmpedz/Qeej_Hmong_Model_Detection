import argparse
from pathlib import Path

from app.application.services.prediction_service import run_inference
from app.application.services.runtime_service import is_allowed_audio_file
from app.infrastructure.config.settings import HOST, MODEL_THRESHOLD, PORT
from app.presentation.http_server import serve
from app.shared.formatting import format_milliseconds, format_seconds


def run_cli_prediction(audio_path, threshold):
    input_path = Path(audio_path).expanduser().resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Cannot find audio file at {input_path}")
    if not is_allowed_audio_file(input_path.name):
        raise ValueError("Only .wav audio files are supported")

    result = run_inference(input_path, threshold=threshold)
    print(f"Check guide animation path: {result.guide_media_path}")
    print(f"Check guide document path: {result.guide_sheet_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="web app for uploading audio and generating Qeej blowing instructions"
    )
    parser.add_argument("--host", default=HOST, help="Host for the local web server")
    parser.add_argument("--port", type=int, default=PORT, help="Port for the local web server")
    parser.add_argument("--predict", help="Run one-shot inference for an audio file instead of starting the web server")
    parser.add_argument("--threshold", type=float, default=MODEL_THRESHOLD, help="Decode threshold with default value is 0.7")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.predict:
        run_cli_prediction(args.predict, threshold=args.threshold)
        return
    serve(host=args.host, port=args.port)
