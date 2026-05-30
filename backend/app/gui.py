import sys
import cv2
from PySide6.QtCore import Qt, QTimer, Slot, Signal
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget
)
from backend.core.pipeline import Phase1Pipeline
from backend.visualization.debug_view import render_debug_view
from queue import Empty


class MilitaryDrillGUI(QMainWindow):
    def __init__(self, pipeline: Phase1Pipeline):
        super().__init__()
        self.pipeline = pipeline
        self.setWindowTitle("Military Drill Intelligence System")
        self.resize(1280, 720)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.init_greeting_screen()
        self.init_main_screen()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def init_greeting_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Military Drill\nIntelligence Engine")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 48, QFont.Bold))
        title.setStyleSheet("color: #4CAF50;")

        subtitle = QLabel("Precision. Compliance. Excellence.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 24))
        subtitle.setStyleSheet("color: #aaaaaa; margin-bottom: 50px;")

        start_btn = QPushButton("INITIALIZE SYSTEM")
        start_btn.setFixedSize(300, 60)
        start_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        start_btn.clicked.connect(self.start_pipeline)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(start_btn)
        
        self.stacked_widget.addWidget(widget)

    def init_main_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #000000;")
        
        # Bottom controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(20, 10, 20, 10)
        
        stop_btn = QPushButton("STOP & EXIT")
        stop_btn.setFixedSize(150, 40)
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        stop_btn.clicked.connect(self.close)
        
        controls_layout.addStretch()
        controls_layout.addWidget(stop_btn)
        
        layout.addWidget(self.video_label, stretch=1)
        layout.addLayout(controls_layout)
        
        self.stacked_widget.addWidget(widget)

    @Slot()
    def start_pipeline(self):
        self.stacked_widget.setCurrentIndex(1)
        self.pipeline.start()
        self.timer.start(30)  # ~33 fps

    @Slot()
    def update_frame(self):
        try:
            # Drain queue to get the latest frame
            result = None
            while not self.pipeline.result_queue.empty():
                result = self.pipeline.result_queue.get_nowait()
            
            if result is not None:
                frame = render_debug_view(result, show_foot_debug=self.pipeline.config.visualization.show_foot_debug)
                # Convert BGR to RGB
                self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = self.current_frame.shape
                bytes_per_line = ch * w
                qt_img = QImage(self.current_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_img)
                # Scale to fit label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.video_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error updating frame: {e}")

    def closeEvent(self, event):
        self.timer.stop()
        self.pipeline.stop()
        event.accept()

def run_gui(pipeline: Phase1Pipeline):
    app = QApplication(sys.argv)
    window = MilitaryDrillGUI(pipeline)
    window.show()
    sys.exit(app.exec())
