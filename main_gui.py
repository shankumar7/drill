import customtkinter as ctk
import cv2
from PIL import Image
import sys

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, parent):
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
        self.video_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.video_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # We need 3 columns for the top row
        # Top row gets weight=1 (smaller height), bottom row gets weight=2 (larger height)
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
        self.data_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.data_frame, text="Real-time Biometric\nCharts Will Appear Here", font=ctk.CTkFont("Inter", 14), text_color="#9ca3af", justify="center").pack(expand=True)
        
        # ==========================================
        # RIGHT: SIDE PANEL
        # ==========================================
        self.side_panel = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0, border_width=1, border_color="#e1e4e8")
        self.side_panel.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(self.side_panel, text="LIVE ANALYTICS", font=ctk.CTkFont("Inter", 18, "bold"), text_color="#111827").pack(pady=(30, 20))
        
        # Status Card
        status_card = ctk.CTkFrame(self.side_panel, fg_color="#f3f4f6", corner_radius=10)
        status_card.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(status_card, text="Drill Stance:", font=ctk.CTkFont("Inter", 12)).pack(anchor="w", padx=15, pady=(15, 0))
        ctk.CTkLabel(status_card, text="SAVDHAN (ATTENTION)", font=ctk.CTkFont("Inter", 16, "bold"), text_color="#059669").pack(anchor="w", padx=15, pady=(0, 15))
        
        # Metrics
        def add_metric(title, val):
            frm = ctk.CTkFrame(self.side_panel, fg_color="transparent")
            frm.pack(fill="x", padx=25, pady=8)
            ctk.CTkLabel(frm, text=title, font=ctk.CTkFont("Inter", 13), text_color="#4b5563").pack(side="left")
            ctk.CTkLabel(frm, text=val, font=ctk.CTkFont("Inter", 13, "bold"), text_color="#111827").pack(side="right")
            
        add_metric("Spine Alignment:", "98% (Perfect)")
        add_metric("Heel Distance:", "0.0 cm")
        add_metric("Feet Angle:", "28°")
        add_metric("Hand Position:", "Locked")
        
        # Divider
        ctk.CTkFrame(self.side_panel, fg_color="#e5e7eb", height=2).pack(fill="x", padx=20, pady=20)
        
        # Action Buttons
        self.record_btn = ctk.CTkButton(self.side_panel, text="START RECORDING", font=ctk.CTkFont("Inter", 14, "bold"), fg_color="#dc2626", hover_color="#b91c1c", corner_radius=8, height=45)
        self.record_btn.pack(fill="x", padx=20, pady=10)
        
        # ==========================================
        # VIDEO CAPTURE LOGIC
        # ==========================================
        # Initialize 4 separate cameras. If a user only has 1, the others will gracefully fail and show NO SIGNAL.
        self.caps = [cv2.VideoCapture(i) for i in range(4)]
        self.update_video_feeds()

    def update_video_feeds(self):
        import numpy as np
        cam_labels = [self.cam1_label, self.cam2_label, self.cam3_label, self.cam4_label]
        # Pushing the sizes to the absolute maximum for a 1080p screen
        sizes = [(950, 600), (460, 310), (460, 310), (460, 310)]
        
        self.current_images = [] # Prevent garbage collection
        
        for i, cap in enumerate(self.caps):
            ret, frame = cap.read()
            if ret:
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


class MinimalistSplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Military Drill Analysis System")
        self.geometry("1100x700")
        self.resizable(True, True)
        self.configure(fg_color="#f0f2f5") 
        
        # Center window
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (1100 / 2))
        y = int((screen_height / 2) - (700 / 2))
        self.geometry(f"1100x700+{x}+{y}")
        
        self.card = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=30, border_width=1, border_color="#e1e4e8")
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.7)
        
        self.content = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content.pack(expand=True, fill="both", padx=80, pady=80)
        
        # Load and set up Logo Image
        self.logo_size = 20
        self.logo_max_size = 120
        try:
            self.logo_pil = Image.open("logo.jpeg")
            self.logo_aspect = self.logo_pil.width / self.logo_pil.height
            self.logo_img = ctk.CTkImage(light_image=self.logo_pil, size=(int(self.logo_size * self.logo_aspect), self.logo_size))
            self.logo_label = ctk.CTkLabel(self.content, text="", image=self.logo_img)
            self.logo_label.pack(anchor="w", pady=(0, 20))
            self.animate_logo()
        except Exception as e:
            print("Could not load logo:", e)
        
        self.org_label = ctk.CTkLabel(
            self.content,
            text="SIMULATION DEVELOPMENT DIVISION (SDD), MCEME",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#8c92a6"
        )
        self.org_label.pack(anchor="w", pady=(0, 30))
        
        self.title_label = ctk.CTkLabel(
            self.content, 
            text="Military Drill\nAnalysis System.", 
            font=ctk.CTkFont(family="Inter", size=46, weight="bold"),
            text_color="#111827",
            justify="left"
        )
        self.title_label.pack(anchor="w", pady=(0, 20))
        
        self.divider = ctk.CTkFrame(self.content, fg_color="#e5e7eb", height=2, width=80)
        self.divider.pack(anchor="w", pady=(0, 25))
        
        desc_text = (
            "A professional evaluation suite designed for rigorous posture and alignment tracking. "
            "Initialize the workspace to begin real-time, camera-based drill compliance assessment."
        )
        self.desc_label = ctk.CTkLabel(
            self.content,
            text=desc_text,
            font=ctk.CTkFont(family="Inter", size=15),
            text_color="#4b5563",
            justify="left",
            wraplength=600
        )
        self.desc_label.pack(anchor="w", pady=(0, 45))
        
        self.launch_btn = ctk.CTkButton(
            self.content,
            text="Start Assessment",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            fg_color="#111827",      
            hover_color="#374151",   
            text_color="#ffffff",
            height=50,
            width=220,
            corner_radius=25,
            command=self.start_system
        )
        self.launch_btn.pack(anchor="w")

    def animate_logo(self):
        if hasattr(self, 'logo_size') and self.logo_size < self.logo_max_size:
            self.logo_size += 5
            self.logo_img.configure(size=(int(self.logo_size * self.logo_aspect), self.logo_size))
            self.after(20, self.animate_logo)

    def start_system(self):
        self.launch_btn.configure(text="Initializing Workspace...", state="disabled", fg_color="#9ca3af")
        self.update()
        
        # Wait a moment for visual feedback, then open dashboard
        self.after(400, self.open_dashboard)
        
    def open_dashboard(self):
        # Hide the splash screen
        self.withdraw()
        
        # Open the new dashboard window
        dashboard = DashboardWindow(self)
        
        # When dashboard closes, close the entire application
        dashboard.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))


if __name__ == "__main__":
    app = MinimalistSplashScreen()
    app.mainloop()
