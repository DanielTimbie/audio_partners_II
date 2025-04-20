# djassistant/analysis/freq_analysis.py
import numpy as np

class FreqAnalyzer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.current_freq = 0.0  # Hz

    def process_frame(self, frame):
        """Analyze the audio frame to find the dominant frequency."""
        # Compute FFT of the frame
        spectrum = np.fft.rfft(frame)  # real FFT for real input
        magnitudes = np.abs(spectrum)
        # Find index of max magnitude (ignoring the DC component at index 0)
        if len(magnitudes) < 2:
            return self.current_freq
        peak_index = np.argmax(magnitudes[1:]) + 1
        # Convert index to frequency in Hz: freq_index * (sample_rate / N)
        freq = peak_index * self.sample_rate / len(frame)
        self.current_freq = freq
        return self.current_freq