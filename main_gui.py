import customtkinter as ctk
import cv2
import threading
import sys
from PIL import Image
import os

# --- UI Configuration ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ProfessionalSplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Military Drill Analysis Engine")
        self.geometry("1100x650")
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (1100 / 2))
        y = int((screen_height / 2) - (650 / 2))
        self.geometry(f"1100x650+{x}+{y}")
        
        # Main Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # -----------------------------------------------------
        # LEFT PANEL: Typography, Context, and Actions
        # -----------------------------------------------------
        self.left_panel = ctk.CTkFrame(self, fg_color="#0d0e15", corner_radius=0)
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        
        # Inner wrapper for left panel to control padding
        self.content_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.content_frame.pack(expand=True, fill="both", padx=60, pady=80)
        
        # Top-left indicator / Version
        self.version_label = ctk.CTkLabel(
            self.content_frame,
            text="SYSTEM V2.4  |  SECURE CONNECTION",
            font=ctk.CTkFont(family="Roboto Mono", size=11, weight="bold"),
            text_color="#00a8ff"
        )
        self.version_label.pack(anchor="w", pady=(0, 20))
        
        # Main Title
        self.title_label = ctk.CTkLabel(
            self.content_frame, 
            text="MILITARY DRILL\nINTELLIGENCE", 
            font=ctk.CTkFont(family="Inter", size=48, weight="bold"),
            text_color="#ffffff",
            justify="left"
        )
        self.title_label.pack(anchor="w", pady=(0, 10))
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.content_frame,
            text="AI-Powered Pose Estimation & Compliance",
            font=ctk.CTkFont(family="Inter", size=18, weight="normal"),
            text_color="#a0aabf"
        )
        self.subtitle_label.pack(anchor="w", pady=(0, 30))
        
        # Description / Mission Statement
        desc_text = (
            "Initiating real-time biomechanical analysis engine. "
            "This system evaluates cadet posture, alignment, and "
            "drill compliance using high-precision spatial tracking "
            "and rule-based heuristics."
        )
        self.desc_label = ctk.CTkLabel(
            self.content_frame,
            text=desc_text,
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#737b8c",
            justify="left",
            wraplength=400
        )
        self.desc_label.pack(anchor="w", pady=(0, 60))
        
        # Launch Button
        self.launch_btn = ctk.CTkButton(
            self.content_frame,
            text="INITIALIZE TRACKER",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            fg_color="#0052cc",
            hover_color="#003d99",
            text_color="#ffffff",
            height=55,
            width=260,
            corner_radius=4,
            command=self.start_system
        )
        self.launch_btn.pack(anchor="w", pady=(0, 20))
        
        # Footer in left panel
        self.footer_label = ctk.CTkLabel(
            self.content_frame,
            text="Crafted by Simulation Development Division (SDD), MCEME",
            font=ctk.CTkFont(family="Inter", size=11, slant="italic"),
            text_color="#464b59"
        )
        self.footer_label.pack(side="bottom", anchor="w")
        
        # -----------------------------------------------------
        # RIGHT PANEL: Branding & Visuals
        # -----------------------------------------------------
        self.right_panel = ctk.CTkFrame(self, fg_color="#14161f", corner_radius=0)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Load the generated AI Logo Image
        image_path = r"C:\Users\AR-ENG\.gemini\antigravity\brain\f733a48f-7c32-48c1-92f6-81717b7a908e\drill_ai_logo_1779683975259.png"
        if os.path.exists(image_path):
            img = Image.open(image_path)
            # Create CTkImage
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 500))
            
            self.image_label = ctk.CTkLabel(self.right_panel, text="", image=self.logo_image)
            self.image_label.pack(expand=True, fill="both", padx=20, pady=20)
        else:
            # Fallback if image path is not found
            self.fallback_label = ctk.CTkLabel(
                self.right_panel,
                text="[ VISUAL ASSET LOAD ERROR ]",
                font=ctk.CTkFont(family="Inter", size=14),
                text_color="#464b59"
            )
            self.fallback_label.pack(expand=True)

    def start_system(self):
        # Update button to show loading state
        self.launch_btn.configure(text="LOADING FEED...", state="disabled", fg_color="#002966")
        self.update()
        
        # Close splash and open camera
        self.after(500, self._launch)
        
    def _launch(self):
        self.destroy()
        threading.Thread(target=run_camera_interface, daemon=True).start()


def run_camera_interface():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Unable to access the camera.")
        sys.exit(1)

    cv2.namedWindow("Military Drill Intelligence - Active Feed", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Military Drill Intelligence - Active Feed", 1024, 768)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Frame capture failed, exiting.")
            break
            
        cv2.imshow("Military Drill Intelligence - Active Feed", frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    app = ProfessionalSplashScreen()
    app.mainloop()
