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
    
    def __process_one_file_audio(
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

        return np.array(X), np.array(y)
    
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

            X, y = self.__process_one_file_audio(audio_file, csv_file)

            X_all.append(X)
            y_all.append(y)

        X_all = np.vstack(X_all)
        y_all = np.hstack(y_all)

        return X_all, y_all



if __name__ == "__main__":
    audio_dir = "../Data/audio/Khèn 1/Đơn_ống"
    labels_dir = "../Data/labels/Khèn 1/Đơn_ống"
    dataModule = DataModule()
    X, y = dataModule.build_dataset(audio_dir, labels_dir)
    
    print("X shape:", X.shape)
    print("y shape:", y.shape)