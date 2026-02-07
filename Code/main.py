
import numpy as np

#preprocessing 
fs = 48000

window_size = int(0.01 * fs)

def split_windows(signal, window_size):
    return [
        signal[i:i+window_size]
        for i in range(0, len(signal) - window_size, window_size)
    ]

def extract_dft(window):
    spectrum = np.abs(np.fft.rfft(window))
    spectrum = spectrum / np.max(spectrum) 
    return spectrum

def suppress_low_amplitudes(spec, threshold_db=50):
    I_threshold = 10 ** (-threshold_db / 20)
    spec[spec < I_threshold] *= 0.2
    return spec

#label data
