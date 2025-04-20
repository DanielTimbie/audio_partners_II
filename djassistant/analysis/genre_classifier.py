# djassistant/analysis/genre_classifier.py
import time

class GenreClassifier:
    def __init__(self):
        self.last_genre = None
        self.last_update = 0
        # (In a real case, load a ML model or initialize features accumulation)

    def process_frame(self, frame, bpm=None, freq=None):
        """
        Process incoming audio frame for genre classification.
        We accumulate features over time and occasionally update the genre prediction.
        """
        genre = self.last_genre or "Unknown"
        current_time = time.time()
        # Only update genre every few seconds to avoid jitter
        if current_time - self.last_update > 5.0:  # update every 5 seconds
            # Placeholder logic: decide genre based on BPM as a simple heuristic
            if bpm:
                if bpm > 125:
                    genre = "Trance"
                elif bpm < 100:
                    genre = "Hip-Hop"
                else:
                    genre = "House"
            else:
                genre = "House"
            self.last_genre = genre
            self.last_update = current_time
        return genre
