import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QProgressBar, QFrame, QScrollArea, QSizePolicy,
                             QListWidget, QPushButton)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QImage, QPixmap, QFont
from backend.core.pipeline import DrillPipeline
from backend.utils.visualization import draw_hud

class CadetMetricWidget(QFrame):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; border-radius: 5px; padding: 5px;")
        
        layout = QVBoxLayout(self)
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("color: #aaa; font-size: 10px; font-weight: bold;")
        
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                background-color: #111;
                height: 15px;
                text-align: center;
                color: white;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
        """)
        layout.addWidget(self.name_label)
        layout.addWidget(self.progress)

    def update_score(self, score):
        self.progress.setValue(int(score))
        if score < 70: color = "#ff0000"
        elif score < 85: color = "#ffaa00"
        else: color = "#00ff00"
        self.progress.setStyleSheet(self.progress.styleSheet().replace("background-color: #00ff00;", f"background-color: {color};")
                                     .replace("background-color: #ffaa00;", f"background-color: {color};")
                                     .replace("background-color: #ff0000;", f"background-color: {color};"))

class DashboardWindow(QMainWindow):
    def __init__(self, source=0):
        super().__init__()
        self.setWindowTitle("MILITARY DRILL AI - COMMAND CENTER")
        self.resize(1400, 950)
        self.setStyleSheet("background-color: #0a0a0a; color: #ffffff;")
        
        self.pipeline = DrillPipeline(source=source)
        self.pipeline.start()
        
        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left Panel: Video Feed & Controls
        left_panel = QVBoxLayout()
        
        # Command Selector
        cmd_layout = QHBoxLayout()
        commands = ["SAVDHAN", "VISHRAM", "AARAM_SE"]
        self.cmd_buttons = {}
        for cmd in commands:
            btn = QPushButton(cmd.replace("_", " "))
            btn.setFixedHeight(40)
            btn.setFont(QFont("Courier New", 12, QFont.Bold))
            btn.setCheckable(True)
            if cmd == "SAVDHAN": btn.setChecked(True)
            btn.setStyleSheet("""
                QPushButton { background-color: #222; color: #888; border: 1px solid #444; }
                QPushButton:checked { background-color: #00ff00; color: #000; border: 1px solid #00ff00; }
            """)
            btn.clicked.connect(lambda checked, c=cmd: self.change_command(c))
            cmd_layout.addWidget(btn)
            self.cmd_buttons[cmd] = btn
        
        left_panel.addLayout(cmd_layout)
        
        self.video_label = QLabel("INITIALIZING COMMAND SENSORS...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #000; border: 2px solid #222;")
        self.video_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        left_panel.addWidget(self.video_label)
        
        # Right Panel: Analytics
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(380)
        self.side_layout = QVBoxLayout(self.side_panel)
        
        title_label = QLabel("DRILL INTELLIGENCE HUD")
        title_label.setFont(QFont("Courier New", 18, QFont.Bold))
        title_label.setStyleSheet("color: #00ff00; border-bottom: 2px solid #00ff00; padding-bottom: 10px;")
        self.side_layout.addWidget(title_label)
        
        self.metrics_scroll = QScrollArea()
        self.metrics_scroll.setWidgetResizable(True)
        self.metrics_scroll.setStyleSheet("border: none; background-color: transparent;")
        self.metrics_container = QWidget()
        self.metrics_layout = QVBoxLayout(self.metrics_container)
        self.metrics_scroll.setWidget(self.metrics_container)
        self.side_layout.addWidget(self.metrics_scroll)
        
        self.metric_widgets = {}
        self.rebuild_metrics("SAVDHAN")
            
        self.side_layout.addWidget(QLabel("SEMANTIC ANALYSIS LOG"))
        self.violation_list = QListWidget()
        self.violation_list.setFixedHeight(150)
        self.violation_list.setStyleSheet("background-color: #111; color: #ffaa00; font-family: Courier New; border: 1px solid #333;")
        self.side_layout.addWidget(self.violation_list)
        
        self.status_label = QLabel("STATUS: STANDBY")
        self.status_label.setFont(QFont("Courier New", 14, QFont.Bold))
        self.status_label.setStyleSheet("padding: 10px; background-color: #111; border: 1px solid #333;")
        self.side_layout.addWidget(self.status_label)
        
        layout.addLayout(left_panel, 7)
        layout.addWidget(self.side_panel, 3)

    def rebuild_metrics(self, mode):
        # Clear existing
        for i in reversed(range(self.metrics_layout.count())): 
            self.metrics_layout.itemAt(i).widget().setParent(None)
        self.metric_widgets = {}
        
        if mode == "SAVDHAN":
            list = ["Heel Alignment", "Foot Angle", "Knee Lock", "Arm Alignment", "Torso Posture", "Shoulder Alignment", "Head Alignment", "Stability", "Symmetry"]
        else:
            list = ["Foot Spacing", "Foot Symmetry", "Knee Lock", "Rear Hand Position", "Balance Score", "Torso Discipline", "Shoulder Alignment", "Head Alignment", "Stability"]
            
        for metric in list:
            widget = CadetMetricWidget(metric.upper())
            self.metrics_layout.addWidget(widget)
            self.metric_widgets[metric] = widget

    def change_command(self, cmd):
        for c, btn in self.cmd_buttons.items():
            btn.setChecked(c == cmd)
        self.pipeline.set_mode(cmd)
        self.rebuild_metrics(cmd)

    def update_frame(self):
        frame, cadets, fps = self.pipeline.get_latest_results()
        if frame is not None:
            hud_frame = draw_hud(frame.copy(), cadets, fps)
            if cadets:
                analysis = cadets[0]['analysis']
                for metric, score in analysis['scores'].items():
                    if metric in self.metric_widgets:
                        self.metric_widgets[metric].update_score(score)
                self.violation_list.clear()
                for v in analysis['violations']:
                    self.violation_list.addItem(f">> {v.upper()}")
                status_color = "#00ff00" if analysis['status'] == "EXCELLENT" else "#ff0000" if analysis['status'] == "INCORRECT" else "#ffaa00"
                self.status_label.setText(f"STATUS: {analysis['status']} ({analysis['overall']:.1f}%)")
                self.status_label.setStyleSheet(f"padding: 10px; background-color: #111; border: 1px solid {status_color}; color: {status_color};")
            rgb_frame = cv2.cvtColor(hud_frame, cv2.COLOR_BGR2RGB)
            q_img = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], rgb_frame.shape[1] * 3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        self.pipeline.stop()
        event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
