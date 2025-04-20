# djassistant/audio/capture.py
import pyaudio
import numpy as np
import threading
import queue

class AudioCapture:
    def __init__(self, sample_rate=44100, channels=1, chunk_size=2048, device_index=None):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_index = device_index
        self._audio_interface = pyaudio.PyAudio()
        self._stream = None
        # Queue to output audio frames to consumers (analysis)
        self.frame_queue = queue.Queue()
        self._stop_flag = False

    def start(self):
        """Start the audio stream in a separate thread."""
        if self._stream is not None:
            return  # already started
        # Open stream with callback that puts data into queue
        self._stream = self._audio_interface.open(format=pyaudio.paInt16,
                                                 channels=self.channels,
                                                 rate=self.sample_rate,
                                                 input=True,
                                                 input_device_index=self.device_index,
                                                 frames_per_buffer=self.chunk_size,
                                                 stream_callback=self._callback)
        self._stream.start_stream()

    def _callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for each audio frame."""
        # Convert byte data to numpy array
        audio_frame = np.frombuffer(in_data, dtype=np.int16).astype(np.float32)
        # If stereo and channels=2, we could downmix to mono:
        # if self.channels == 2:
        #     audio_frame = audio_frame.reshape(-1, 2).mean(axis=1)
        if not self._stop_flag:
            try:
                self.frame_queue.put(audio_frame, block=False)
            except queue.Full:
                pass  # if queue is full, drop the frame (to avoid lag)
        return (None, pyaudio.paContinue)

    def stop(self):
        """Stop the audio stream."""
        self._stop_flag = True
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        self._audio_interface.terminate()