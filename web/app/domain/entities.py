from dataclasses import dataclass
from pathlib import Path


@dataclass
class Segment:
    start_frame: int
    end_frame: int
    start_second: float
    end_second: float
    label: str


@dataclass
class InferenceResult:
    source_name: str
    upload_path: Path
    guide_media_path: Path
    guide_sheet_path: Path
    segments: list[Segment]
    active_segments: list[Segment]
    total_windows: int
    duration_seconds: float
    sample_rate: int
    predict_workers: int
    timings_ms: dict[str, float]
