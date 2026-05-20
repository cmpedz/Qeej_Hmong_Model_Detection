import os
import shutil
from pathlib import Path

import librosa


os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

APP_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = Path(__file__).resolve().parents[3]
PROJECT_ROOT = WEB_ROOT

MODEL_PATH = WEB_ROOT / "model" / "fold_3.keras"
UPLOAD_DIR = WEB_ROOT / "uploads"
OUTPUT_DIR = WEB_ROOT / "outputs"

HOST = "127.0.0.1"
PORT = 8000
MODEL_THRESHOLD = 0.7
TARGET_SAMPLE_RATE = 48000
MAX_PREDICT_WORKERS = max(1, min(2, os.cpu_count() or 1))
MIN_WINDOWS_PER_WORKER = 10

WINDOWS_TO_SECOND = 0.1
HOP_LENGTH = 512
N_BINS = 168
BINS_PER_OCTAVE = 24
FMIN = librosa.note_to_hz("C3")

LABELS_DICT = {
    "P1": 0,
    "P2": 1,
    "P3": 2,
    "T1": 3,
    "T2": 4,
    "T3": 5,
    "silence": 6,
}
LABELS_ARR = list(LABELS_DICT.keys())


def ensure_runtime_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clear_runtime_dirs():
    ensure_runtime_dirs()
    for runtime_dir in (UPLOAD_DIR, OUTPUT_DIR):
        for child in runtime_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
                continue
            child.unlink()
