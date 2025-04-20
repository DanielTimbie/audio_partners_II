# djassistant/analysis/audio_analyzer.py
from .beat_tracker import BeatTracker
from .freq_analysis import FreqAnalyzer
from .genre_classifier import GenreClassifier

class AudioAnalyzer:
    def __init__(self, sample_rate=44100):
        self.beat_tracker = BeatTracker(sample_rate=sample_rate)
        self.freq_analyzer = FreqAnalyzer(sample_rate=sample_rate)
        self.genre_classifier = GenreClassifier()

    def process_frame(self, frame):
        """Process a new audio frame through all analysis sub-modules."""
        beat = self.beat_tracker.process_frame(frame)        # True if beat detected
        bpm = self.beat_tracker.tempo                        # current BPM
        freq = self.freq_analyzer.process_frame(frame)       # dominant frequency
        genre = self.genre_classifier.process_frame(frame, bpm=bpm, freq=freq)
        # Return a dictionary of results
        return {"beat": beat, "bpm": bpm, "freq": freq, "genre": genre}