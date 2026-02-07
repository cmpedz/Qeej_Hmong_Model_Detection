import sounddevice as sd
from pathlib import Path
import numpy as np
import soundfile as sf
import pandas as pd
import re


def DetectSoundOfWindows(audioPath):
    signal, fs = sf.read(audioPath)

    # 10 ms window
    window_size = int(0.01 * fs)

    windows = [
        signal[i:i+window_size]
        for i in range(0, len(signal) - window_size, window_size)
    ]

    for k, w in enumerate(windows):
        start_time = k * 0.01
        end_time = start_time + 0.01

        print(f"\nWindow {k} | {start_time:.3f}s – {end_time:.3f}s")
        sd.play(w, fs)
        sd.wait()
        cmd = input("Enter = next | q = quit: ")
        if cmd.lower() == 'q':
            break

def CreateCsvOfAudio(audioPath, saveFolder = "Đơn_ống"):
    signal, fs = sf.read(audioPath)
    window_size = int(0.01 * fs)
    hop_size = window_size
    save_path = "../Data/labels/" + saveFolder + "/"

    num_windows = (len(signal) - window_size) // hop_size

    rows = []
    for i in range(num_windows):
        start = i * hop_size
        rows.append({
            "window_idx": i,
            "start_time": start / fs,
            "end_time": (start + window_size) / fs,
            "label": "UNLABELED"
        })

    df = pd.DataFrame(rows)
    audio_name = Path(audioPath).name
    print("check audio name: ", audio_name)
    csv_name = audio_name.replace(".wav",".csv")
    df.to_csv(save_path + csv_name, index=False)

if __name__ == "__main__":
    audio_path_test = "../Data/audio/Đơn_ống/drone_gần.wav"
    CreateCsvOfAudio(audio_path_test)
