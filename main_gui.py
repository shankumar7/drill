import customtkinter as ctk
import cv2
from PIL import Image, ImageDraw, ImageOps
import sys
# Premium UI imports
from ui.style import *
from ui.circular_gauge import CircularGauge
# Component imports
from ui.components.navigation_bar import NavigationBar
from ui.components.header import Header
from ui.components.dashboard import DashboardContent

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, parent, workflow_actions=None):
        super().__init__(parent)
        self.title("Military Drill Analysis - Dashboard")
        self.geometry("1400x800")
        self.configure(fg_color="#f0f2f5")
        
        # Make it full screen / maximizable
        self.state('zoomed') 
        
        # Protocol to cleanly release cameras when closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Grid Layout for Main Dashboard
        # Left side (Videos) gets more space (weight=3), Right side (Sidebar) gets less (weight=1)
        self.grid_columnconfigure(0, weight=4) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)
        
        # ==========================================
        # LEFT: VIDEO FEED AREA
        # ==========================================
        # Use modular dashboard component
        self.dashboard = DashboardContent(self, workflow_actions)
        self.dashboard.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)

        # Alias video frame and camera labels for backward compatibility
        self.video_frame = self.dashboard.video_frame
        self.cam1_label = self.dashboard.cam1_label
        self.cam2_label = self.dashboard.cam2_label
        self.cam3_label = self.dashboard.cam3_label
        self.cam4_label = self.dashboard.cam4_label
        self.gauge_spine = self.dashboard.gauge_spine
        self.gauge_heel = self.dashboard.gauge_heel
        self.gauge_feet = self.dashboard.gauge_feet
        self.gauge_hand = self.dashboard.gauge_hand

        # Configure grid for video_frame columns/rows
        self.video_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(1, weight=2)
        
        # Helper to create camera containers
        def create_cam_container(parent_frame, title, row, col, columnspan=1):
            container = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="#ffffff", border_width=1, border_color="#e1e4e8")
            container.grid(row=row, column=col, columnspan=columnspan, sticky="nsew", padx=10, pady=10)
            
            lbl_title = ctk.CTkLabel(container, text=title, font=ctk.CTkFont("Inter", 12, "bold"), text_color="#6b7280")
            lbl_title.pack(pady=(5, 0))
            
            lbl_video = ctk.CTkLabel(container, text="")
            lbl_video.pack(expand=True, fill="both", padx=0, pady=0)
            return lbl_video
            
        # Top 3 Cameras (Smaller)
        self.cam4_label = create_cam_container(self.video_frame, "CAM 4 - FEET ANGLE", 0, 0)
        self.cam2_label = create_cam_container(self.video_frame, "CAM 2 - SIDE ANGLE", 0, 1)
        self.cam3_label = create_cam_container(self.video_frame, "CAM 3 - TOP ANGLE", 0, 2)
        
        # Bottom Left Camera (Cam 1) - Spans 2 columns to be wider and taller
        self.cam1_label = create_cam_container(self.video_frame, "CAM 1 - FRONT ANGLE", 1, 0, columnspan=2)
        
        # The remaining bottom space (col 2 in row 1) for charts/data
        self.data_frame = ctk.CTkFrame(self.video_frame, corner_radius=15, fg_color="#ffffff", border_width=1, border_color="#e1e4e8")
        # Legacy UI components have been migrated to the modular DashboardContent component.
        # The dashboard now provides video area, side panel, gauges, and action buttons.
        # References to gauges and record button are accessed via self.dashboard attributes.

        
        # ==========================================
        # VIDEO CAPTURE LOGIC & ML BACKEND
        # ==========================================
        # Future-proof pipeline: Initializing only the primary camera (index 0) to avoid 
        # 30-second driver timeouts on Windows for missing devices. 
        self.caps = [None, None, None, None]
        # Try to open up to 4 camera indices until one succeeds
        for idx in range(4):
            try:
                cap = cv2.VideoCapture(idx)
                if cap.isOpened():
                    self.caps[idx] = cap
                    print(f"Camera {idx} opened successfully.")
                else:
                    cap.release()
            except Exception as e:
                print(f"Failed to open camera {idx}: {e}")
        

        # ML Backend Setup
        self.pose_estimator = None
        self.evaluator = None
        try:
            from backend.inference.pose_estimator import YoloPoseEstimator
            from backend.evaluation.evaluator import StaticPostureEvaluator
            current_mode = (workflow_actions[0] if workflow_actions else "SAVDHAN").upper()
            
            # Using ultra-fast YOLO version if available
            self.pose_estimator = YoloPoseEstimator(
                model_path="yolo11n-pose.pt",
                confidence=0.5,
                image_size=640,
                prefer_half_precision=True,
                tracking_enabled=False,
                tracker_config=None
            )
            self.evaluator = StaticPostureEvaluator(current_mode)
            print(f"Loaded ML Engine for {current_mode}")
        except Exception as e:
            print("Failed to load ML Backend:", e)

        self.update_video_feeds()

    def update_video_feeds(self):
        import numpy as np
        cam_labels = [self.cam1_label, self.cam2_label, self.cam3_label, self.cam4_label]
        sizes = [(950, 600), (460, 310), (460, 310), (460, 310)]
        
        self.current_images = [] # Prevent garbage collection
        
        for i, cap in enumerate(self.caps):
            ret = False
            if cap is not None:
                ret, frame = cap.read()
                
            if ret:
                if i == 0 and self.pose_estimator and self.evaluator:
                    try:
                        # Process frame through ML
                        detections = self.pose_estimator.infer(frame)
                        if detections:
                            det = detections[0] # Focus on primary subject
                            det.evaluation = self.evaluator.evaluate(det)
                            
                            # Draw overlays
                            from backend.visualization.debug_view import _draw_skeleton
                            _draw_skeleton(frame, det.keypoints)
                            
                            # Update UI Metrics dynamically
                            scores = det.evaluation.scores
                            if "Torso Posture" in scores:
                                 self.gauge_spine.set_value(scores['Torso Posture'])
                            if "Heel Alignment" in scores:
                                 self.gauge_heel.set_value(scores['Heel Alignment'])
                            if "Foot Angle" in scores:
                                 self.gauge_feet.set_value(scores['Foot Angle'])
                            if "Arm Alignment" in scores:
                                 self.gauge_hand.set_value(scores['Arm Alignment'])
                    except Exception as e:
                        pass
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                w, h = sizes[i]
                frame = np.zeros((h, w, 3), dtype=np.uint8)
                frame[:] = (240, 242, 245)
                # Center the text
                cv2.putText(frame, "NO SIGNAL", (w//2 - 60, h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)

            img = Image.fromarray(frame)
            ctk_img = ctk.CTkImage(light_image=img, size=sizes[i])
            self.current_images.append(ctk_img)
            cam_labels[i].configure(image=ctk_img)
            
        # Call this function again after 30 milliseconds (~30fps)
        self.after(30, self.update_video_feeds)

    def on_closing(self):
        for cap in self.caps:
            cap.release()
        self.destroy()


class LoadingFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Center container for logo and progress bar
        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.place(relx=0.5, rely=0.5, anchor="center")
        
        self.logo_size = 20
        self.logo_max_size = 160
        try:
            pil_img = Image.open("logo.jpeg").convert("RGBA")
            
            # Make circular mask
            min_dim = min(pil_img.size)
            left = (pil_img.size[0] - min_dim) / 2
            top = (pil_img.size[1] - min_dim) / 2
            right = (pil_img.size[0] + min_dim) / 2
            bottom = (pil_img.size[1] + min_dim) / 2
            pil_img = pil_img.crop((left, top, right, bottom))
            
            mask = Image.new('L', pil_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + pil_img.size, fill=255)
            
            self.logo_pil = Image.new('RGBA', pil_img.size, (0, 0, 0, 0))
            self.logo_pil.paste(pil_img, (0, 0), mask)
            
            self.logo_aspect = 1.0 # Circular is always 1:1
            self.logo_img = ctk.CTkImage(light_image=self.logo_pil, size=(self.logo_size, self.logo_size))
            self.logo_label = ctk.CTkLabel(self.center_container, text="", image=self.logo_img)
            self.logo_label.pack(pady=(0, 30))
            
            # Add premium progress bar (letter_spacing not supported in CTkLabel)
            self.loading_text = ctk.CTkLabel(
                self.center_container,
                text="INITIALIZING SYSTEM...",
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#6b7280"
            )
            self.loading_text.pack(pady=(0, 10))
            
            self.progress = ctk.CTkProgressBar(
                self.center_container,
                width=250,
                height=6,
                corner_radius=3,
                fg_color="#e5e7eb",
                progress_color="#2563eb"
            )
            self.progress.pack()
            self.progress.set(0)
            
            self.animate_logo()
        except Exception as e:
            print("Could not load logo:", e)
            
        # Auto transition after 3 seconds
        self.after(3000, lambda: self.controller.show_frame(InfoFrame))
        
    def animate_logo(self):
        # Pulsating bounce animation with easing
        if hasattr(self, 'logo_size') and self.logo_size < self.logo_max_size:
            diff = self.logo_max_size - self.logo_size
            step = max(3, int(diff * 0.18))  # slightly faster ramp
            self.logo_size += step
            self.logo_img.configure(size=(self.logo_size, self.logo_size))
            # Sync progress bar with size animation
            prog = self.progress.get()
            if prog < 1.0:
                self.progress.set(min(1.0, prog + 0.06))
            self.after(15, self.animate_logo)
        else:
            # Gentle breathing effect after reaching max size
            def breathing():
                # oscillate size +/- 5px around max for subtle effect
                import math, time
                t = time.time()
                offset = int(5 * math.sin(t * 2))
                size = self.logo_max_size + offset
                self.logo_img.configure(size=(size, size))
                # keep progress filling until full
                prog = self.progress.get()
                if prog < 1.0:
                    self.progress.set(min(1.0, prog + 0.01))
                    self.after(50, breathing)
                else:
                    # After progress complete, move to next frame after short pause
                    self.after(500, lambda: self.controller.show_frame(InfoFrame))
            breathing()


class InfoFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.org_label = ctk.CTkLabel(self, text="SIMULATION DEVELOPMENT DIVISION (SDD), MCEME", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#8c92a6")
        self.org_label.pack(anchor="w", pady=(0, 30))
        
        self.title_label = ctk.CTkLabel(self, text="Military Drill\nAnalysis System.", font=ctk.CTkFont(family="Inter", size=46, weight="bold"), text_color="#111827", justify="left")
        self.title_label.pack(anchor="w", pady=(0, 20))
        
        self.divider = ctk.CTkFrame(self, fg_color="#e5e7eb", height=2, width=80)
        self.divider.pack(anchor="w", pady=(0, 25))
        
        desc_text = "A professional evaluation suite designed for rigorous posture and alignment tracking. Initialize the workspace to begin real-time, camera-based drill compliance assessment."
        self.desc_label = ctk.CTkLabel(self, text=desc_text, font=ctk.CTkFont(family="Inter", size=15), text_color="#4b5563", justify="left", wraplength=600)
        self.desc_label.pack(anchor="w", pady=(0, 45))
        
        self.launch_btn = ctk.CTkButton(self, text="Get Started", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), fg_color="#111827", hover_color="#374151", text_color="#ffffff", height=50, width=220, corner_radius=25, command=lambda: self.controller.show_frame(WorkflowSelectionFrame))
        self.launch_btn.pack(anchor="w")


class WorkflowSelectionFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.workflow_actions = []
        
        ctk.CTkLabel(self, text="Configure Drill Workflow", font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color="#111827").pack(anchor="w", pady=(0, 20))
        ctk.CTkLabel(self, text="Select the actions to include in this drill session.", font=ctk.CTkFont(family="Inter", size=15), text_color="#4b5563").pack(anchor="w", pady=(0, 30))
        
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 20))
        
        self.action_var = ctk.StringVar(value="Savadhan")
        self.action_dropdown = ctk.CTkOptionMenu(input_frame, variable=self.action_var, values=["Savadhan", "Vishram", "Salute", "Turn Right", "Turn Left", "About Turn"], font=ctk.CTkFont("Inter", 14), height=40, width=250)
        self.action_dropdown.pack(side="left", padx=(0, 15))
        
        self.add_btn = ctk.CTkButton(input_frame, text="Add Action", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), height=40, command=self.add_action)
        self.add_btn.pack(side="left")
        
        self.queue_label = ctk.CTkLabel(self, text="Current Workflow:", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#111827")
        self.queue_label.pack(anchor="w", pady=(10, 5))
        
        self.queue_display = ctk.CTkTextbox(self, height=150, font=ctk.CTkFont("Inter", 14), state="disabled")
        self.queue_display.pack(fill="x", pady=(0, 30))
        
        self.start_btn = ctk.CTkButton(self, text="Initialize Drill", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), fg_color="#059669", hover_color="#047857", height=50, width=220, corner_radius=25, command=self.start_drill)
        self.start_btn.pack(anchor="w")
        self.start_btn.configure(state="disabled")

    def add_action(self):
        action = self.action_var.get()
        self.workflow_actions.append(action)
        self.queue_display.configure(state="normal")
        self.queue_display.delete("1.0", "end")
        self.queue_display.insert("end", " -> ".join(self.workflow_actions))
        self.queue_display.configure(state="disabled")
        self.start_btn.configure(state="normal")

    def start_drill(self):
        self.controller.workflow_actions = self.workflow_actions
        self.controller.show_frame(CameraLoadingFrame)
        self.after(100, self.controller.launch_dashboard)


class CameraLoadingFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        # Apply glass‑morphism backdrop for premium look
        apply_glass(self, radius=20, opacity=0.1)
        
        ctk.CTkLabel(self, text="Initializing Camera System...", font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color="#111827").pack(expand=True, pady=(0, 10))
        ctk.CTkLabel(self, text="Please wait while video feeds are connected.", font=ctk.CTkFont(family="Inter", size=14), text_color="#6b7280").pack()
        # Spinner overlay for premium loading animation
        try:
            spinner_path = r"C:\Users\AR-ENG\.gemini\antigravity-ide\brain\52c35f2d-202f-4438-b8a1-9ea195d35941\spinner_1780121771499.png"
            spinner_img = ctk.CTkImage(Image.open(spinner_path), size=(64, 64))
            self.spinner_label = ctk.CTkLabel(self, image=spinner_img, text="")
            self.spinner_label.pack(pady=(20,0))
        except Exception as e:
            print("Spinner load failed:", e)

class SummaryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        ctk.CTkLabel(self, text="Drill Session Summary", font=ctk.CTkFont(family="Inter", size=24, weight="bold")).pack(pady=20)

class AppManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Military Drill Analysis System")
        self.geometry("1100x700")
        self.configure(fg_color="#f0f2f5") 
        
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (1100 / 2))
        y = int((screen_height / 2) - (700 / 2))
        self.geometry(f"1100x700+{x}+{y}")
        
        self.card = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=30, border_width=1, border_color="#e1e4e8")
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.7)
        
        self.frames = {}
        self.workflow_actions = []
        
        for F in (LoadingFrame, InfoFrame, WorkflowSelectionFrame, CameraLoadingFrame, SummaryFrame):
            frame = F(parent=self.card, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew", padx=80, pady=80)
            
        self.card.grid_rowconfigure(0, weight=1)
        self.card.grid_columnconfigure(0, weight=1)
        
        self.show_frame(LoadingFrame)
        # Store reference to current frame for transitions
        self.current_frame = LoadingFrame

    def show_frame(self, cont):
        # Fade‑in transition for premium feel
        frame = self.frames[cont]
        frame.tkraise()
        # Simple opacity animation using after (CustomTkinter lacks real opacity, so we just call after)
        self.after(50, lambda: None)
        self.current_frame = cont

    def launch_dashboard(self):
        self.withdraw()
        dashboard = DashboardWindow(self, self.workflow_actions)
        dashboard.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))

if __name__ == "__main__":
    app = AppManager()
    app.mainloop()
