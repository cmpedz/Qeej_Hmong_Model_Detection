import numpy as np
import pandas as pd
import librosa
from pathlib import Path

class DataModule:

    def __extract_dft(self, window):
        spectrum = np.abs(np.fft.rfft(window))
        spectrum = spectrum / np.max(spectrum) 
        return spectrum

    def __suppress_low_amplitudes(self, spec, threshold_db=50):
        I_threshold = 10 ** (-threshold_db / 20)
        spec[spec < I_threshold] *= 0.2
        return spec
    def __get_spectrum_of_window(self, window):

        spectrum = self.__extract_dft(window)

        #preprocessing
        standard_spectrum = self.__suppress_low_amplitudes(spectrum)

        return standard_spectrum
    
    def process_one_file_audio(
        self,
        audio_path,
        csv_path,
        sample_rate=48000,
        window_size=0.01
    ):
        #load audio
        audio, sr = librosa.load(audio_path, sr=sample_rate, mono=True)

        samples_per_window = int(sample_rate * window_size)

        # Load CSV
        df = pd.read_csv(csv_path)
        X = []
        y = []

        # preparing data 
        for _, row in df.iterrows():
            start_sample = int(row["start_time"] * sample_rate)
            end_sample = start_sample + samples_per_window

            if end_sample > len(audio):
                continue

            window = audio[start_sample:end_sample]
            spectrum = self.__get_spectrum_of_window(window)

            X.append(spectrum)
            y.append(row["label"])

        # reducing silence sample
        silence_label = "silence"
        flag = True
        start_index = 0
        end_index = len(y) - 1
        max_silence_label = 3
        X_reduced = []
        y_reduced = []
        while flag:

            if y[start_index] == silence_label:
                start_index += 1

            if y[end_index] == silence_label:
                end_index -= 1

            if y[start_index] != silence_label and y[end_index] != silence_label:
                X_reduced = X[start_index:end_index + 1]
                y_reduced = y[start_index:end_index + 1]


                num_start_silence = start_index - 0
                num_end_silence = len(y) - 1 - end_index

                if num_start_silence > max_silence_label:
                    num_start_silence = max_silence_label

                if num_end_silence > max_silence_label:
                    num_end_silence = max_silence_label

                for i in np.arange(num_start_silence):
                    X_reduced.append(X[i])
                    y_reduced.append(y[i])

                for i in np.arange(num_end_silence):
                    end_index = len(y) - 1 - i
                    X_reduced.append(X[end_index])
                    y_reduced.append(y[end_index])

                flag = False
                


        return np.array(X_reduced), np.array(y_reduced)
    
    def build_dataset(self, audio_dir, csv_dir):
        audio_dir = Path(audio_dir)
        csv_dir = Path(csv_dir)

        X_all = []
        y_all = []

        for audio_file in audio_dir.glob("*.wav"):
            csv_file = csv_dir / (audio_file.stem + ".csv")

            if not csv_file.exists():
                print(f"unable to find csv file for {audio_file.name}")
                continue

            X, y = self.process_one_file_audio(audio_file, csv_file)

            X_all.append(X)
            y_all.append(y)

        X_all = np.vstack(X_all)
        y_all = np.hstack(y_all)

        return X_all, y_all



if __name__ == "__main__":
    # audio_dir = "../Data/audio/Khèn 1/Đơn_ống"
    # labels_dir = "../Data/labels/Khèn 1/Đơn_ống"
    # dataModule = DataModule()
    # X, y = dataModule.build_dataset(audio_dir, labels_dir)
    
    # print("X shape:", X.shape)
    # print("y shape:", y.shape)

    audio_path = "../Data/audio/Khèn 3 (vừa)/Đơn ống/drone_gan.wav"
    csv_path = "../Data/labels/Khèn 3 (vừa)/Đơn_ống/drone_gan.csv"
    data_module = DataModule()
    X, y = data_module.process_one_file_audio(audio_path, csv_path)

    print(y)