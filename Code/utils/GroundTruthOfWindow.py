import sounddevice as sd
from pathlib import Path
import numpy as np
import soundfile as sf
import pandas as pd
import matplotlib.pyplot as plt
import re


def DrawWaveFormOfAudio(audio_path):
    signal, fs = sf.read(audio_path)
    time = np.arange(len(signal)) / fs
    window_size = 0.01
    audio_name = Path(audio_path).name

    # Vẽ waveform
    plt.figure(figsize=(12, 4))
    plt.plot(time, signal)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.title("Waveform of audio signal")
    plt.xticks(np.arange(0, time[-1], window_size))
    plt.tight_layout()

    for t in np.arange(0, time[-1], window_size):
        plt.axvline(t, linewidth=0.3)
    plt.title(audio_name)
    plt.show()


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

def CreateCsvOfAllAudiosInAFolder(folder_path, save_folder= "Đơn_ống"):
    folder_path = Path(folder_path)
    wav_files = list(folder_path.glob("*.wav"))
    for wav_file in wav_files:
        print("create csv file for audio file:", wav_file)
        CreateCsvOfAudio(wav_file, save_folder)

if __name__ == "__main__":

    # tạo csv để gán nhãn cho dữ liệu audio tương ứng
    # audio_path_test = "../Data/audio/Khèn 5 (to)/Đa ống/6_ống"
    # CreateCsvOfAllAudiosInAFolder(folder_path=audio_path_test, save_folder="Khèn 5 (to)/Đa_ống/6_ống")

    audio_path = "../Data/audio/Khèn 5 (to)/Đa ống/6_ống/6_ong_xa2.wav"
    DrawWaveFormOfAudio(audio_path)
