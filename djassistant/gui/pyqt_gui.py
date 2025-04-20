import sys
import random
import numpy as np
import queue
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QProgressBar
)
from PyQt5.QtGui import QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QTimer


class BeatCircle(QWidget):
    def __init__(self):
        super().__init__()
        self.color = QColor("gray")
        self.setMinimumHeight(200)

    def flash(self, color="cyan"):
        self.color = QColor(color)
        QTimer.singleShot(100, lambda: self.set_color("gray"))
        self.update()

    def set_color(self, color):
        self.color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.color))
        size = min(self.width(), self.height())
        painter.drawEllipse((self.width()-size)//2, (self.height()-size)//2, size, size)


class DJAssistantApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DJ Assistant (PyQt Edition)")
        self.setStyleSheet("background-color: black; color: white;")
        self.init_ui()
        self.player = None
        self.analyzer_queue = None

    def init_ui(self):
        layout = QVBoxLayout()

        self.bpm_label = QLabel("BPM: --")
        self.genre_label = QLabel("Genre: --")
        self.freq_label = QLabel("Freq: --")
        for lbl in [self.bpm_label, self.genre_label, self.freq_label]:
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 20px;")
            layout.addWidget(lbl)

        self.visual = BeatCircle()
        layout.addWidget(self.visual)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)
        layout.addWidget(self.play_button)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                background-color: #222;
            }
            QProgressBar::chunk {
                background-color: #00f;
            }
        """)
        layout.addWidget(self.progress)

        self.setLayout(layout)

        self.seek_timer = QTimer()
        self.seek_timer.timeout.connect(self.update_seek_slider)
        self.seek_timer.start(200)

    def set_sources(self, audio_player, analyzer_queue):
        self.player = audio_player
        self.analyzer_queue = analyzer_queue

        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self.poll_analyzer)
        self.analysis_timer.start(50)

    def poll_analyzer(self):
        if self.analyzer_queue is None:
            return
        try:
            result = self.analyzer_queue.get_nowait()
            self.update_display(result)
        except queue.Empty:
            pass

    def update_display(self, analysis_result):
        def scalar(x):
            if isinstance(x, np.ndarray):
                return x.item()
            return x

        if analysis_result:
            bpm = scalar(analysis_result.get("bpm"))
            freq = scalar(analysis_result.get("freq") or analysis_result.get("dominant_frequency"))
            genre = analysis_result.get("genre")

            beat = analysis_result.get("beat")
            if isinstance(beat, dict):
                beat = beat.get("beat", False)
            beat = scalar(beat)

            self.bpm_label.setText(f"BPM: {int(bpm)}" if bpm else "BPM: --")
            self.freq_label.setText(f"Freq: {int(freq)} Hz" if freq else "Freq: --")
            self.genre_label.setText(f"Genre: {genre}" if genre else "Genre: --")

            if beat:
                self.visual.flash("cyan")
            else:
                color = "blue" if freq and int(freq) % 2 == 0 else "red"
                self.visual.set_color(color)

    def toggle_play(self):
        if not self.player:
            return
        if self.player.is_playing():
            self.player.pause()
            self.play_button.setText("Play")
        else:
            self.player.play()
            self.play_button.setText("Pause")

    def update_seek_slider(self):
        if self.player:
            self.progress.setValue(self.player.get_position())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DJAssistantApp()
    win.show()
    sys.exit(app.exec_())
