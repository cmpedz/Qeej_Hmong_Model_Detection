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
        raise ValueError("Only .wav audio files are supported.")

    result = run_inference(input_path, threshold=threshold)
    print(f"Guide animation: {result.guide_media_path}")
    print(f"Guide document: {result.guide_sheet_path}")
    print(f"Detected active segments: {len(result.active_segments)}")
    print(f"Predict workers: {result.predict_workers}")
    for key, value in result.timings_ms.items():
        print(f"  {key}: {format_milliseconds(value)}")
    for segment in result.active_segments[:10]:
        print(f"  {format_seconds(segment.start_second)}s - {format_seconds(segment.end_second)}s: {segment.label}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Local MKQH web app for uploading audio and generating Qeej blowing instructions."
    )
    parser.add_argument("--host", default=HOST, help="Host for the local web server.")
    parser.add_argument("--port", type=int, default=PORT, help="Port for the local web server.")
    parser.add_argument("--predict", help="Run one-shot inference for an audio file instead of starting the web server.")
    parser.add_argument("--threshold", type=float, default=MODEL_THRESHOLD, help="Decode threshold. Default is 0.8.")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.predict:
        run_cli_prediction(args.predict, threshold=args.threshold)
        return
    serve(host=args.host, port=args.port)
