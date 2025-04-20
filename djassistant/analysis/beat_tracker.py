# djassistant/analysis/beat_tracker.py
import numpy as np
import librosa
import time

class BeatTracker:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.buffer_size = 5 * sample_rate  # 5 seconds buffer
        self.buffer = np.zeros(self.buffer_size, dtype=np.float32)
        self.beat_times = []
        self.last_checked = time.time()
        self.start_time = time.time()
        self.tempo = 120  # Default tempo

    def process_frame(self, frame):
        # Shift in new frame
        L = len(frame)
        self.buffer = np.roll(self.buffer, -L)
        self.buffer[-L:] = frame

        # Every 1s, re-run beat detection
        now = time.time()
        if now - self.last_checked > 1.0:
            # Only analyze if we have enough non-zero data
            if np.sum(np.abs(self.buffer)) > 0.01:
                try:
                    tempo, beat_frames = librosa.beat.beat_track(
                        y=self.buffer, 
                        sr=self.sample_rate,
                        hop_length=512
                    )
                    if tempo > 0:
                        self.tempo = tempo
                    beat_times = librosa.frames_to_time(beat_frames, sr=self.sample_rate)
                    if len(beat_times) > 0:
                        self.beat_times = beat_times
                except Exception as e:
                    print(f"Beat detection error: {e}")
            self.last_checked = now

        # Determine if we're near a beat (within 100ms window)
        elapsed = now - self.start_time
        beat_detected = False
        
        if len(self.beat_times) > 0:
            # Calculate position in the beat pattern
            beat_period = 60.0 / self.tempo
            position_in_pattern = elapsed % beat_period
            
            # Check if we're within 100ms of a beat
            beat_detected = position_in_pattern < 0.1 or position_in_pattern > beat_period - 0.1

        return {
            "beat": beat_detected,
            "bpm": self.tempo
        }
