# djassistant/audio/fileplayer.py
import soundfile as sf
import sounddevice as sd
import numpy as np
import threading
import queue
import time

class AudioFilePlayer:
    def __init__(self, filepath, chunk_size=2048):
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.frame_queue = queue.Queue()
        self._stop_flag = False
        self._paused = False
        self._file = sf.SoundFile(self.filepath, 'r')
        self.sample_rate = self._file.samplerate  # Use native sample rate
        print("Sample rate:", self.sample_rate)
        self.channels = 1  # force mono for simplicity
        self.current_frame = 0
        self.total_frames = len(self._file)

    def start(self):
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        print("Starting audio playback thread")
        with sd.OutputStream(samplerate=self.sample_rate, channels=1) as stream:
            print(f"Output stream using sample rate: {self.sample_rate}")
            while not self._stop_flag:
                if self._paused:
                    time.sleep(0.05)
                    continue

                data = self._file.read(self.chunk_size, dtype='float32')
                self.current_frame = self._file.tell()

                if len(data) == 0:
                    print("End of file, looping")
                    self._file.seek(0)
                    continue

                # Downmix stereo to mono
                if data.ndim > 1:
                    data = data.mean(axis=1)

                stream.write(data)

                try:
                    self.frame_queue.put_nowait(data.copy())  # safe copy
                except queue.Full:
                    pass

                time.sleep(len(data) / self.sample_rate)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def is_paused(self):
        return self._paused

    def seek(self, fraction):
        frame = int(fraction * self.total_frames)
        self._file.seek(frame)
        self.current_frame = frame

    def stop(self):
        self._stop_flag = True

    def play(self):
        """Adapter method to match GUI expectations"""
        self.resume()

    def is_playing(self):
        """Adapter method to match GUI expectations"""
        return not self._paused

    def get_position(self):
        """Return current position as 0-100 value for slider"""
        return int((self.current_frame / self.total_frames) * 100)

    def get_duration(self):
        """Return duration as 100 for slider scale"""
        return 100  # always return as 100% scale (0-100 slider)


