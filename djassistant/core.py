import sys
import queue
import threading
from PyQt5.QtWidgets import QApplication

from djassistant.audio.fileplayer import AudioFilePlayer
from djassistant.audio.capture import AudioCapture
from djassistant.analysis.audio_analyzer import AudioAnalyzer
from djassistant.gui.pyqt_gui import DJAssistantApp

def run_app(audio_file):
    audio_source = AudioFilePlayer(audio_file, chunk_size=2048)
    analyzer = AudioAnalyzer(sample_rate=audio_source.sample_rate)
    analysis_queue = queue.Queue(maxsize=10)

    # Start audio
    audio_source.start()

    # Start analysis thread
    def audio_analysis_loop():
        while True:
            frame = audio_source.frame_queue.get()
            if frame is None:
                break
            if frame.ndim == 2:
                frame = frame.mean(axis=1)
            result = analyzer.process_frame(frame)
            try:
                analysis_queue.put(result, timeout=0.1)
            except queue.Full:
                try:
                    analysis_queue.get_nowait()
                    analysis_queue.put(result, timeout=0.1)
                except queue.Empty:
                    pass

    threading.Thread(target=audio_analysis_loop, daemon=True).start()

    # Start PyQt GUI
    app = QApplication(sys.argv)
    gui = DJAssistantApp()
    gui.set_sources(audio_source, analysis_queue)
    gui.show()
    sys.exit(app.exec_())

def main():
    """Entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description="DJ Assistant")
    parser.add_argument("--file", type=str, required=True, help="Path to .wav file")
    
    args = parser.parse_args()
    
    sys.exit(run_app(args.file))

if __name__ == "__main__":
    main()
