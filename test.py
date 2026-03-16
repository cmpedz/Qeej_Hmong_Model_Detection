# %% [markdown]
# # Set up library

# %%
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
import h5py
import os
import librosa
import json
import unicodedata
import pandas as pd






# %% [markdown]
# # Main

# %%


# %% [markdown]
# ## Analyzing spectrogram of audio by CQT

# %%
results = {}
save_path = "./Experiments/Results_from_Cqt_(bins per octave = 48)"


# %%

def preprocess_audio(audio):

    # normalize amplitude
    audio = audio / (np.max(np.abs(audio)) + 1e-8)

    return audio

def analyze_spectrogram_by_CQT_of_audio(audio_path, img_path):

    y, sr = librosa.load(audio_path, sr=None)

    # y = preprocess_audio(y)

    hop_length = 512


    C = librosa.cqt(
        y,
        sr=sr,
        hop_length=hop_length,
        fmin=librosa.note_to_hz('C3'),
        n_bins=252,
        bins_per_octave=36
    )

    n_frames = C.shape[1]

    frame_time = hop_length / sr

    times = np.arange(n_frames) * frame_time


    C_db = librosa.amplitude_to_db(np.abs(C))

    plt.figure(figsize=(12,6))

    librosa.display.specshow(
            C_db,
            sr=sr,
            hop_length=hop_length,
            x_axis='time',
            y_axis='cqt_note'
    )

    plt.title(audio_path)

    for t in times:
        plt.axvline(x=t, color='white', alpha = 0.5, linewidth=1)

    step = max(1, n_frames // 20)

    frame_ticks = np.arange(0, n_frames, step)
    frame_tick_times = frame_ticks * frame_time

    plt.xticks(frame_tick_times, frame_ticks)

    plt.xlabel("Frame index")

    plt.colorbar(format="%+2.0f dB")

    plt.tight_layout()

    print("Show!")

    plt.show()

    # plt.savefig(img_path, dpi=300)

def analyzing_spectrograms_for_audios_in_folder(audio_folder):

    audio_folder_name = "audio"
    img_folder_name = "spectrograms"

    if os.path.exists(audio_folder):
        for root, dirs, files in os.walk(audio_folder):
            for file in files:
                if file.endswith(".wav"):
                    img_root = root.replace(audio_folder_name, img_folder_name)
                if os.path.exists(img_root):
                    img_file_name = file.replace(".wav", ".png")
                    img_path = os.path.join(img_root, img_file_name)
                    audio_path = os.path.join(root, file)
                    analyze_spectrogram_by_CQT_of_audio(audio_path, img_path)
                    
                    
                else:
                    print(img_root, "doesnt exists !")
                    
    else:
        print("Cant find folder at", audio_folder)

    

# %%

# def detect_multi_pitchs_of_audio(audio_path):

#     model_output, midi_data, note_events = predict(audio_path)

#     freqs = []

#     for note in note_events:
#         pitch = note[2]
#         freq = 440 * 2 ** ((pitch - 69)/12)
#         freqs.append(freq)

#     results[audio_path] = freqs


# %% [markdown]
# ## Helper to create csv file

# %%
def create_label_template(audio_path, output_csv, hop_length=512):

    y, sr = librosa.load(audio_path, sr=None)

    duration = librosa.get_duration(y=y, sr=sr)

    frame_time = hop_length / sr

    total_frames = int(duration / frame_time)

    frames = np.arange(total_frames)

    start_times = frames * frame_time
    end_times = start_times + frame_time

    df = pd.DataFrame({
        "frame": frames,
        "start_time": start_times,
        "end_time": end_times,
        "label": "Default"
    })

    df.to_csv(output_csv, index=False)

def create_labels_for_audios_in_folder(audio_folder):

    audio_folder_name = "audio"
    csv_folder_name = "frame_labels"

    if os.path.exists(audio_folder):
        for root, dirs, files in os.walk(audio_folder):
            for file in files:
                if file.endswith(".wav"):
                    csv_root = root.replace(audio_folder_name, csv_folder_name)
                if os.path.exists(csv_root):
                    csv_file_name = file.replace(".wav", ".csv")
                    csv_path = os.path.join(csv_root, csv_file_name)
                    audio_path = os.path.join(root, file)
                    create_label_template(audio_path, csv_path)
                    
                    
                else:
                    print(csv_root, "doesnt exists !")
                    
    else:
        print("Cant find folder at", audio_folder)


# %% [markdown]
# ## assess all audio

# %%
#  # read data from drive
# audio_data_set_paths =  ["./Data/audio/Khèn 1/Đơn_ống",
#                          "./Data/audio/Khèn 2 (vừa)/Đơn ống",
#                          "./Data/audio/Khèn 3 (vừa)/Đơn ống",
#                          "./Data/audio/Khèn 4 (to)/Đơn ống",
#                          "./Data/audio/Khèn 5 (to)/Đơn ống",
#                          "./Real Data/Khèn 1/Đơn âm",
#                          "./Real Data/Khèn 2/Đơn âm",
#                          "./Real Data/Khèn 3/Đơn âm",
#                          "./Real Data/Khèn 4/Đơn âm"]

# index = 0
# for audio_data_set_path in audio_data_set_paths:
#     if os.path.exists(audio_data_set_path):
#       for root, dirs, files in os.walk(audio_data_set_path):
#         for file in files:
#           if file.endswith(".wav"):
#             audio_file_path = os.path.join(root, file)
#             file_name = file.replace(".wav","") + f"from qeej {index}"
#             analyze_spectrogram_by_CQT_of_audio(audio_file_path, file_name)
#       index +=1
#     else:
#       print("Cant find folder at", audio_data_set_path)

# save_path = "./Experiments/results.json"
# with open(save_path, "w", encoding="utf-8") as f:
#     json.dump(results, f, ensure_ascii=False, indent=4)

# audio_file_paths = ["./Data/audio/Khèn 1/Đơn_ống/trái_1_gần.wav", 
#                     "./Data/audio/Khèn 1/Đơn_ống/trái_1_xa.wav", 
#                     "./Data/audio/Khèn 1/Đơn_ống/trái 1 xa 2.wav",
#                     "./Data/audio/Khèn 2 (vừa)/Đơn ống/1_trái_gần.wav",
#                     "./Data/audio/Khèn 2 (vừa)/Đơn ống/1_trái_xa.wav",
#                     "./Data/audio/Khèn 3 (vừa)/Đơn ống/1_trai_gan.wav",
#                     "./Data/audio/Khèn 3 (vừa)/Đơn ống/1_trai_xa.wav",
#                     "./Data/audio/Khèn 3 (vừa)/Đơn ống/1_trai_xa2.wav"
#                     ]
    



# %% [markdown]
# ## Save Spectrograms of audios into folder

# %%
# audios_paths = ["./Data/audio/Khèn 1", "./Data/audio/Khèn 2 (vừa)","./Data/audio/Khèn 3 (vừa)", "./Data/audio/Khèn 4 (to)", "./Data/audio/Khèn 5 (to)"]

# for audios_path in audios_paths:
#     analyzing_spectrograms_for_audios_in_folder(audios_path)

audio_path = "./Data/audio/Khèn 4 (to)/Đa_ống/2_ống/2_phai_3_trai_xa2.wav"

analyze_spectrogram_by_CQT_of_audio(audio_path, "")
    


