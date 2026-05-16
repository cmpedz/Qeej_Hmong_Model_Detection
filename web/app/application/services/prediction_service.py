import uuid
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

import numpy as np

from app.domain.audio_analysis import (
    build_segments,
    build_windows,
    decode_label,
    extract_dual_cqt,
    merge_segments,
    normalize_predicted_label,
    postprocess_probabilities,
    resolve_predict_workers,
)
from app.domain.entities import InferenceResult
from app.infrastructure.config.settings import (
    HOP_LENGTH,
    MAX_PREDICT_WORKERS,
    MODEL_THRESHOLD,
    OUTPUT_DIR,
    ensure_runtime_dirs,
)
from app.infrastructure.ml.model_loader import get_model
from app.infrastructure.rendering.guide_renderer import render_guide_animation, render_guide_sheet
from app.shared.formatting import sanitize_filename


def predict_chunk(model_input_chunk):
    model = get_model()
    return model.predict(model_input_chunk, verbose=0)


def predict_windows(model_input, max_workers=MAX_PREDICT_WORKERS):
    if len(model_input) == 0:
        return np.empty((0, 0), dtype=np.float32)

    worker_count = resolve_predict_workers(len(model_input), max_workers=max_workers)
    if worker_count == 1:
        return predict_chunk(model_input)

    window_chunks = [chunk for chunk in np.array_split(model_input, worker_count, axis=0) if len(chunk) > 0]
    with ThreadPoolExecutor(max_workers=len(window_chunks), thread_name_prefix="mkqh-predict") as executor:
        chunk_predictions = list(executor.map(predict_chunk, window_chunks))
    return np.concatenate(chunk_predictions, axis=0)


def run_inference(audio_path, threshold=MODEL_THRESHOLD, max_workers=MAX_PREDICT_WORKERS):
    total_started_at = perf_counter()
    timings_ms = {}
    ensure_runtime_dirs()

    step_started_at = perf_counter()
    cqt, sr, duration_seconds = extract_dual_cqt(audio_path)
    timings_ms["extract_features"] = (perf_counter() - step_started_at) * 1000

    step_started_at = perf_counter()
    windows, frame_ranges = build_windows(cqt, sr)
    timings_ms["build_windows"] = (perf_counter() - step_started_at) * 1000
    if len(frame_ranges) == 0:
        raise ValueError("Doan am thanh qua ngan de du doan.")
    if windows.ndim != 3:
        raise ValueError("Khong the tao cua so dac trung tu doan am thanh dau vao.")

    model_input = np.expand_dims(windows, axis=-1)
    worker_count = resolve_predict_workers(len(model_input), max_workers=max_workers)

    step_started_at = perf_counter()
    y_prob = predict_windows(model_input, max_workers=max_workers)
    timings_ms["predict"] = (perf_counter() - step_started_at) * 1000

    step_started_at = perf_counter()
    processed_prob = postprocess_probabilities(y_prob)
    timings_ms["postprocess"] = (perf_counter() - step_started_at) * 1000

    step_started_at = perf_counter()
    predicted_labels = [
        normalize_predicted_label(decode_label(prob_per_window, threshold=threshold))
        for prob_per_window in processed_prob
    ]
    timings_ms["decode_labels"] = (perf_counter() - step_started_at) * 1000

    step_started_at = perf_counter()
    per_window_segments = build_segments(frame_ranges, predicted_labels, sr)
    timings_ms["build_segments"] = (perf_counter() - step_started_at) * 1000

    step_started_at = perf_counter()
    merged_segments = merge_segments(per_window_segments)
    active_segments = [segment for segment in merged_segments if segment.label.lower() != "silence"]
    timings_ms["merge_segments"] = (perf_counter() - step_started_at) * 1000

    output_run_dir = OUTPUT_DIR / f"{sanitize_filename(audio_path.stem)}_{uuid.uuid4().hex[:8]}"
    output_run_dir.mkdir(parents=True, exist_ok=True)
    guide_media_path = output_run_dir / "guide_animation.gif"
    guide_sheet_path = output_run_dir / "guide_sheet.pdf"

    result = InferenceResult(
        source_name=audio_path.name,
        upload_path=audio_path,
        guide_media_path=guide_media_path,
        guide_sheet_path=guide_sheet_path,
        segments=merged_segments,
        active_segments=active_segments,
        total_windows=len(per_window_segments),
        duration_seconds=duration_seconds,
        sample_rate=sr,
        predict_workers=worker_count,
        timings_ms=timings_ms,
    )

    step_started_at = perf_counter()
    render_guide_animation(result, guide_media_path)
    timings_ms["render_animation"] = (perf_counter() - step_started_at) * 1000

    step_started_at = perf_counter()
    render_guide_sheet(result, guide_sheet_path)
    timings_ms["render_guide_sheet"] = (perf_counter() - step_started_at) * 1000
    timings_ms["total_inference"] = (perf_counter() - total_started_at) * 1000

    return result
