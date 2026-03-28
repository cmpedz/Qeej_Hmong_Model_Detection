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
folder_save = "Khèn 9/Đa_ống/3_ống"
save_img_path = "./Experiments/result from cqt of a song/Ntiv 1/Img"
save_pitch_json_path = f"./Experiments/result from extracting pitches of qeejs Hmong/{folder_save}/Pitches"
save_note_json_path = f"./Experiments/result from extracting pitches of qeejs Hmong/{folder_save}/Json"
save_note_imge_path = f"./Experiments/result from extracting pitches of qeejs Hmong/{folder_save}/Img_with_threhold_0.4"

hop_length = 512
n_bins=84
bins_per_octave=12
fmin=librosa.note_to_hz('C1')

def get_notes_of_a_audio(notes, counts, file_name):

    note_midi = [librosa.note_to_midi(n) for n in notes]
    sorted_idx = np.argsort(note_midi)
    notes = notes[sorted_idx]
    counts = counts[sorted_idx]    

    plt.figure(figsize=(14,6))
    plt.bar(notes, counts, width=0.5)

    plt.xlabel("Notes")
    plt.ylabel("Counts")
    plt.title("Histogram of Notes")

    plt.xticks(rotation=45)
    plt.tight_layout()
    save_path = os.path.join(save_note_imge_path, file_name)
    plt.savefig(save_path , dpi=300)
    plt.close()

def get_CQT_of_a_audio(audio_path):
    y, sr = librosa.load(audio_path, sr=None)

    C = librosa.cqt(
        y,
        sr=sr,
        hop_length=hop_length,
        fmin=fmin,
        n_bins=n_bins,
        bins_per_octave=bins_per_octave
    )

    return C, sr

def extract_topk_pitch_to_json( cqt, sr, file_name, k=7, threshold = 0.1):

    n_frames = cqt.shape[1]
    max_energy = np.max(cqt)

    freqs = librosa.cqt_frequencies(
        n_bins=n_bins,
        fmin=fmin,
        bins_per_octave=bins_per_octave
    )


    times = librosa.frames_to_time(
        np.arange(n_frames),
        sr=sr
    )

    results = []

    notes = []

    for t in range(n_frames):
        frame = cqt[:, t]

        if frame.size == 0:
            continue

        top_k_idx = np.argsort(frame)[-k:][::-1]

        pitches = []
        for i in top_k_idx:
            current_energy = frame[i]
            if float(current_energy) < threshold * max_energy:
                continue

            pitches.append({
                "hz": float(freqs[i]),
                "note": librosa.hz_to_note(freqs[i]),
                "energy": float(frame[i])
            })

            notes.append(librosa.hz_to_note(freqs[i]))
        
        if len(pitches) > 0:
            results.append({
                "frame": int(t),
                "time": float(times[t]),
                "pitches": pitches
            })


    notes, counts = np.unique(notes, return_counts=True)
    note_count_dict = dict(zip(notes, counts))

    get_notes_of_a_audio(notes, counts, file_name.replace(".json", ".png"))

    # note_count_dict = {
    #     str(k): int(v) for k, v in note_count_dict.items()
    # }

    # save_pitch_path = os.path.join(save_pitch_json_path, file_name)
    # save_note_path = os.path.join(save_note_json_path, file_name)
    # with open(save_pitch_path, "w", encoding="utf-8") as f:
    #     json.dump(results, f, indent=4, ensure_ascii=False)

    # with open(save_note_path, "w", encoding="utf-8") as f:
    #     json.dump(note_count_dict, f, indent=4, ensure_ascii=False)

def extract_pitches_from_audios(audio_folder_path):
    if os.path.exists(audio_folder_path):
        for root, dirs, files in os.walk(audio_folder_path):
            for file in files:
                if file.endswith(".wav"):
                    json_file_name = file.replace(".wav",".json")
                    audio_path = os.path.join(root, file)
                    cqt, sr = get_CQT_of_a_audio(audio_path)
                    extract_topk_pitch_to_json(cqt, sr, json_file_name, threshold=0.2)
                    
    else:
        print("Cant find folder at", audio_folder_path)


#extracting pitches from each pile of qeej
audio_folder_path = "./Real Data/Khèn 4/Đa âm/3 ống"
extract_pitches_from_audios(audio_folder_path)



## Extracting pitches from a song
# audio_path = "./Data/audio/Giai điệu/Khèn 1/ntiv.wav"

# C, sr = get_CQT_of_a_audio(audio_path)

# n_frames = C.shape[1]

# frame_time = hop_length / sr

# time_analyzed = 1 #s

# quantities_frame_analyzed = time_analyzed // frame_time

   
# C_db = librosa.amplitude_to_db(np.abs(C))
# print("Check C_db.shape(1):", C_db.shape[1])

# #save pitches extracted into json file
# extract_topk_pitch_to_json(C_db, n_frames)

# # save cqt spectrograms into folder
# for i in np.arange(0, n_frames, quantities_frame_analyzed):

#     print(int(i), int(i+quantities_frame_analyzed))
#     C_db_analyzed = C_db[:, int(i):int(i+quantities_frame_analyzed)]
#     start_time_analyzed = i/quantities_frame_analyzed
#     last_time_analyzed = (i+quantities_frame_analyzed) / quantities_frame_analyzed
#     title = f"Analyze cqt from {start_time_analyzed} s - {last_time_analyzed} s"

#     print(C_db_analyzed)
#     plt.figure(figsize=(12,6))

#     librosa.display.specshow(
#             C_db_analyzed,
#             sr=sr,
#             hop_length=hop_length,
#             x_axis='time',
#             y_axis='cqt_note'
#     )

#     img_path_new = save_img_path + f"/{title}.png"
#     plt.title(title)
#     plt.colorbar(format="%+2.0f dB")
#     plt.tight_layout()
#     plt.savefig(img_path_new, dpi=300)




    


