# djassistant/gui/dance_animator.py
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt
import os

class DanceAnimator(QLabel):
    def __init__(self, folder, frames=16):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.frames = []
        self.current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._next_frame)
        self._load_frames(folder, frames)
        self._current_bpm = None

    def _load_frames(self, folder, count):
        self.frames.clear()
        for i in range(count):
            path = os.path.join(folder, f"frame_{i:02d}.png")
            pix = QPixmap(path)
            if not pix.isNull():
                self.frames.append(pix)
        if self.frames:
            self.setPixmap(self.frames[0])

    def _next_frame(self):
        if not self.frames:
            return
        self.current_index = (self.current_index + 1) % len(self.frames)
        self.setPixmap(self.frames[self.current_index])

    def start(self, bpm):
        if not self.frames:
            return
        interval = int((60 / bpm) * 1000 / len(self.frames))  # ms between frames
        self.timer.start(interval)

    def stop(self):
        self.timer.stop()

    def update_bpm(self, bpm):
        if not self.frames:
            return
        if self._current_bpm == bpm:
            return  # No change needed
        self._current_bpm = bpm
        interval = int((60 / bpm) * 1000 / len(self.frames))
        self.timer.start(interval)

    def switch_dance(self, new_folder, frame_count=16):
        self.stop()
        self._load_frames(new_folder, frame_count)
        self.current_index = 0
        self.start(120)  # default bpm until next update
