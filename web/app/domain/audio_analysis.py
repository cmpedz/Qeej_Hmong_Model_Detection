import math

import librosa
import numpy as np

from app.domain.entities import Segment
from app.infrastructure.config.settings import (
    BINS_PER_OCTAVE,
    FMIN,
    HOP_LENGTH,
    LABELS_ARR,
    LABELS_DICT,
    MIN_WINDOWS_PER_WORKER,
    N_BINS,
    TARGET_SAMPLE_RATE,
    WINDOWS_TO_SECOND,
)


def encode_label(label_str):
    vec = np.zeros(len(LABELS_DICT))
    if label_str is None:
        return vec

    normalized = str(label_str).strip()
    if normalized == "":
        return vec

    labels = [label.strip() for label in normalized.split(",")]
    for label in labels:
        if label in LABELS_DICT:
            vec[LABELS_DICT[label]] = 1
    return vec


def decode_label(vec, threshold=0.5):
    labels = []
    for index, value in enumerate(vec):
        if value > threshold:
            labels.append(LABELS_ARR[index])
    if not labels:
        return ""
    return ", ".join(labels)


def extract_dual_cqt(audio_path):
    y, sr = librosa.load(audio_path, sr=TARGET_SAMPLE_RATE)
    cqt = librosa.cqt(
        y,
        sr=sr,
        hop_length=HOP_LENGTH,
        fmin=FMIN,
        n_bins=N_BINS,
        bins_per_octave=BINS_PER_OCTAVE,
    )
    mag = np.abs(cqt)
    log_mag = librosa.amplitude_to_db(mag)
    return log_mag, sr, len(y) / float(sr)


def smoothing(label_probs, label_idx, on_threshold=0.7, off_threshold=0.05):
    if LABELS_ARR[label_idx] == "silence":
        return np.zeros(len(label_probs))

    smoothing_label_probs = np.zeros(len(label_probs))
    on_idx = -1

    for index in np.arange(len(label_probs)):
        if label_probs[index] >= on_threshold and on_idx < 0:
            on_idx = index
            continue

        if (label_probs[index] < off_threshold or index == len(label_probs) - 1) and on_idx >= 0:
            off_idx = index
            smoothing_label_probs[on_idx:off_idx] = 1
            on_idx = -1

    return smoothing_label_probs


def filling_and_removing(label_probs, label_idx, gap_durations=3, max_frames_exist=3):
    if LABELS_ARR[label_idx] == "silence":
        return np.zeros(len(label_probs))

    label_probs = label_probs.copy()
    label_active_idx = np.where(label_probs == 1)[0]
    gaps = np.diff(label_active_idx)

    for index, gap in enumerate(gaps):
        if gap > 1 and gap <= gap_durations:
            start_idx = label_active_idx[index]
            end_idx = start_idx + gap
            label_probs[start_idx : end_idx + 1] = 1

    index = 0
    while index < len(label_probs):
        if label_probs[index] == 0:
            index += 1
            continue

        frames = 0
        start_idx = index
        while index < len(label_probs) and label_probs[index] == 1:
            frames += 1
            end_idx = index
            index += 1

        if frames < max_frames_exist:
            label_probs[start_idx : end_idx + 1] = 0

    return label_probs


def filling_silence_label(label_probs_per_frame):
    label_probs_per_frame = label_probs_per_frame.copy()
    label_active_idx = np.where(label_probs_per_frame == 1)[0]
    if len(label_active_idx) == 0:
        silence_idx = LABELS_DICT["silence"]
        label_probs_per_frame[silence_idx] = 1
    return label_probs_per_frame


def postprocess_probabilities(y_prob):
    y_prob = y_prob.T
    y_prob = [smoothing(label_prob, label_idx) for label_idx, label_prob in enumerate(y_prob)]
    y_prob = [filling_and_removing(label_prob, label_idx) for label_idx, label_prob in enumerate(y_prob)]
    y_prob = np.array(y_prob).T
    y_prob = [filling_silence_label(labels_prob_each_frame) for labels_prob_each_frame in y_prob]
    return np.array(y_prob)


def build_windows(cqt, sr):
    window_size = int(WINDOWS_TO_SECOND * sr / HOP_LENGTH)
    total_frames = cqt.shape[1]
    windows = []
    frame_ranges = []

    for start_frame in range(0, total_frames - window_size + 1, window_size):
        end_frame = start_frame + window_size
        window = cqt[:, start_frame:end_frame]
        if window.shape[1] != window_size:
            continue
        windows.append(window)
        frame_ranges.append((start_frame, end_frame))

    return np.array(windows), frame_ranges


def normalize_predicted_label(label_text):
    normalized = str(label_text).strip()
    return normalized if normalized else "silence"


def resolve_predict_workers(total_windows, max_workers):
    if total_windows <= 0 or max_workers <= 1 or total_windows < MIN_WINDOWS_PER_WORKER:
        return 1

    workers_by_data = math.ceil(total_windows / float(MIN_WINDOWS_PER_WORKER))
    return max(1, min(max_workers, total_windows, workers_by_data))


def build_segments(frame_ranges, predicted_labels, sample_rate):
    segments = []
    for (start_frame, end_frame), predicted_label in zip(frame_ranges, predicted_labels):
        segments.append(
            Segment(
                start_frame=start_frame,
                end_frame=end_frame,
                start_second=start_frame * HOP_LENGTH / float(sample_rate),
                end_second=end_frame * HOP_LENGTH / float(sample_rate),
                label=predicted_label,
            )
        )
    return segments


def merge_segments(segments):
    if not segments:
        return []

    merged = [
        Segment(
            start_frame=segments[0].start_frame,
            end_frame=segments[0].end_frame,
            start_second=segments[0].start_second,
            end_second=segments[0].end_second,
            label=segments[0].label,
        )
    ]

    for segment in segments[1:]:
        last_segment = merged[-1]
        contiguous = segment.start_frame == last_segment.end_frame
        same_label = segment.label == last_segment.label
        if contiguous and same_label:
            last_segment.end_frame = segment.end_frame
            last_segment.end_second = segment.end_second
            continue

        merged.append(
            Segment(
                start_frame=segment.start_frame,
                end_frame=segment.end_frame,
                start_second=segment.start_second,
                end_second=segment.end_second,
                label=segment.label,
            )
        )

    return merged
