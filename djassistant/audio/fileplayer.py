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
        
        # Open the file and get its native sample rate
        self._file = sf.SoundFile(self.filepath, 'r')
        self.sample_rate = self._file.samplerate  # Use the file's actual sample rate
        print(f"Audio file sample rate: {self.sample_rate} Hz")
        
        self.channels = 1  # force mono for simplicity
        self.current_frame = 0
        self.total_frames = len(self._file)

    def start(self):
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        """Read audio frames from file and put them in the queue."""
        print(f"Starting audio playback thread with sample rate: {self.sample_rate} Hz")
        
        with sd.OutputStream(samplerate=self.sample_rate, channels=1) as stream:
            print(f"Output stream initialized with sample rate: {self.sample_rate} Hz")
            
            self._file.seek(0)
            while not self._stop_flag:
                if self._paused:
                    time.sleep(0.1)
                    continue
                    
                # Read a chunk of audio with explicit float32 dtype
                frames = self._file.read(self.chunk_size, dtype='float32')
                if len(frames) == 0:
                    # End of file
                    if self.loop:
                        self._file.seek(0)
                        continue
                    else:
                        break
                    
                # Convert to mono if needed
                if frames.ndim > 1:
                    frames = frames.mean(axis=1)
                    
                # Put in queue and update position
                self.frame_queue.put(frames)
                self.current_frame += len(frames)
                
                # Update stream
                stream.write(frames)

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


