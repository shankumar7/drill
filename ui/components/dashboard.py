"""ui/components/dashboard.py

DashboardContent component consolidates the main video feed area, side panel with gauges,
and action buttons into a reusable module.
It mirrors the original layout from `main_gui.py` but is encapsulated for modularity.
"""

import customtkinter as ctk
from ui.style import BG_COLOR, CARD_COLOR, ACCENT_GOLD, INTER_BOLD, INTER_REGULAR
from ui.circular_gauge import CircularGauge

class DashboardContent(ctk.CTkFrame):


    Parameters
    ----------
    master : widget
        Parent widget.
    workflow_actions : list, optional
        Actions passed from the workflow selection to display in the status card.
    open_settings_callback : callable, optional
        Function to call when user clicks the Settings button.
    """
    def __init__(self, master, workflow_actions=None, open_settings_callback=None, *args, **kwargs):
        super().__init__(master, fg_color=BG_COLOR, *args, **kwargs)
        self.open_settings_callback = open_settings_callback

        # ---------- Video feed area (left side) ----------
        self.video_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.video_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure grid: 2 columns (sidebar thumbnails, main view)
        self.video_frame.grid_columnconfigure(0, weight=1)  # sidebar
        self.video_frame.grid_columnconfigure(1, weight=3)  # main view
        self.video_frame.grid_rowconfigure(0, weight=1)

        # Sidebar with three thumbnail cameras
        self.sidebar = ctk.CTkFrame(self.video_frame, fg_color="transparent")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        self.sidebar.grid_rowconfigure((0,1,2), weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Main camera view (large)
        self.main_view = ctk.CTkFrame(self.video_frame, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew")
        self.main_view.grid_rowconfigure(0, weight=1)
        self.main_view.grid_columnconfigure(0, weight=1)

        # Helper to create a camera container
        def create_cam_container(parent, title, row, col, is_main=False):
            container = ctk.CTkFrame(parent, corner_radius=15, fg_color="#ffffff", border_width=1, border_color="#e1e4e8")
            # Bind click to select this camera as main view
            lbl.bind("<Button-1>", lambda e, i=idx: master.select_camera(i))
            self.thumb_cam_labels.append(lbl)

        # Create the large main camera view (shows selected camera)
        self.main_label = create_cam_container(self.main_view, "SELECTED CAMERA", 0, 0, is_main=True)

        # Placeholder for charts/data (right side of dashboard, not part of video_frame)
        self.data_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#ffffff", border_width=1, border_color="#e1e4e8")
        self.data_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        ctk.CTkLabel(
            self.data_frame,
            text="Real‑time Biometric\nCharts Will Appear Here",
            font=ctk.CTkFont("Inter", 14),
            text_color="#9ca3af",
            justify="center",
        ).pack(expand=True)

        # ---------------------------- Side panel (right side) ----------------------------
        self.side_panel = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0, border_width=1, border_color="#e1e4e8")
        self.side_panel.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(self.side_panel, text="LIVE ANALYTICS", font=ctk.CTkFont("Inter", 18, "bold"), text_color="#111827").pack(pady=(30, 20))

        # Status Card
        status_card = ctk.CTkFrame(self.side_panel, fg_color="#f3f4f6", corner_radius=10)
        status_card.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(status_card, text="Drill Sequence:", font=ctk.CTkFont("Inter", 12)).pack(anchor="w", padx=15, pady=(15, 0))
        actions_text = " -> ".join(workflow_actions) if workflow_actions else "SAVDHAN"
        ctk.CTkLabel(
            status_card,
            text=actions_text,
            font=ctk.CTkFont("Inter", 14, "bold"),
            text_color="#059669",
            wraplength=250,
        ).pack(anchor="w", padx=15, pady=(0, 15))

        # Gauge container
        gauge_size = 120
        gauge_thickness = 12
        self.gauge_container = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        self.gauge_container.pack(fill="x", padx=20, pady=10)
        self.gauge_spine = CircularGauge(self.gauge_container, size=gauge_size, thickness=gauge_thickness, fg_color=ACCENT_GOLD, bg_color=CARD_COLOR)
        self.gauge_spine.pack(pady=8)
        self.gauge_heel = CircularGauge(self.gauge_container, size=gauge_size, thickness=gauge_thickness, fg_color=ACCENT_GOLD, bg_color=CARD_COLOR)
        self.gauge_heel.pack(pady=8)
        self.gauge_feet = CircularGauge(self.gauge_container, size=gauge_size, thickness=gauge_thickness, fg_color=ACCENT_GOLD, bg_color=CARD_COLOR)
        self.gauge_feet.pack(pady=8)
        self.gauge_hand = CircularGauge(self.gauge_container, size=gauge_size, thickness=gauge_thickness, fg_color=ACCENT_GOLD, bg_color=CARD_COLOR)
        self.gauge_hand.pack(pady=8)

        # Divider
        ctk.CTkFrame(self.side_panel, fg_color="#e5e7eb", height=2).pack(fill="x", padx=20, pady=20)

        # Action button (placeholder for future recording)
        self.record_btn = ctk.CTkButton(
            self.side_panel,
            text="START RECORDING",
            font=ctk.CTkFont("Inter", 14, "bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            corner_radius=8,
            height=45,
        )
        self.record_btn.pack(fill="x", padx=20, pady=10)

        # Settings button
        self.settings_btn = ctk.CTkButton(
            self.side_panel,
            text="SETTINGS",
            font=ctk.CTkFont("Inter", 12, "bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            corner_radius=6,
            height=35,
            command=self.open_settings
        )
        self.settings_btn.pack(fill="x", padx=20, pady=5)

        # Layout weights for the three columns (video_frame, data_frame, side_panel)
        self.grid_columnconfigure(0, weight=3)  # video area
        self.grid_columnconfigure(1, weight=1)  # data frame
        self.grid_columnconfigure(2, weight=1)  # side panel
        self.grid_rowconfigure(0, weight=1)

    def open_settings(self):
        """Invoke the callback provided by the parent window to show settings UI."""
        if self.open_settings_callback:
            self.open_settings_callback()


    
    Parameters
    ----------
    master : widget
        Parent widget.
    workflow_actions : list, optional
        Actions passed from the workflow selection to display in the status card.
    """

        super().__init__(master, fg_color=BG_COLOR, *args, **kwargs)

        # ----------------------------
        # Video feed area (left side)
        # ----------------------------
        self.video_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.video_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Configure grid for the three‑by‑two layout used previously
        self.video_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(1, weight=2)

        def create_cam_container(parent, title, row, col, columnspan=1):
            container = ctk.CTkFrame(parent, corner_radius=15, fg_color="#ffffff", border_width=1, border_color="#e1e4e8")
            container.grid(row=row, column=col, columnspan=columnspan, sticky="nsew", padx=10, pady=10)
            lbl_title = ctk.CTkLabel(container, text=title, font=INTER_BOLD, text_color="#6b7280")
            lbl_title.pack(pady=(5, 0))
            lbl_video = ctk.CTkLabel(container, text="")
            lbl_video.pack(expand=True, fill="both", padx=0, pady=0)
            return lbl_video

        # Top three smaller cameras
        self.cam4_label = create_cam_container(self.video_frame, "CAM 4 - FEET ANGLE", 0, 0)
        self.cam2_label = create_cam_container(self.video_frame, "CAM 2 - SIDE ANGLE", 0, 1)
        self.cam3_label = create_cam_container(self.video_frame, "CAM 3 - TOP ANGLE", 0, 2)
        # Bottom left large camera spans two columns
        self.cam1_label = create_cam_container(self.video_frame, "CAM 1 - FRONT ANGLE", 1, 0, columnspan=2)
        # Placeholder for charts/data (bottom‑right cell)
        self.data_frame = ctk.CTkFrame(self.video_frame, corner_radius=15, fg_color="#ffffff", border_width=1, border_color="#e1e4e8")
        self.data_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(
            self.data_frame,
            text="Real‑time Biometric\nCharts Will Appear Here",
            font=ctk.CTkFont("Inter", 14),
            text_color="#9ca3af",
            justify="center",
        ).pack(expand=True)

        # ----------------------------
        # Side panel (right side)
        # ----------------------------
        self.side_panel = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0, border_width=1, border_color="#e1e4e8")
        self.side_panel.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(self.side_panel, text="LIVE ANALYTICS", font=ctk.CTkFont("Inter", 18, "bold"), text_color="#111827").pack(pady=(30, 20))

        # Status Card
        status_card = ctk.CTkFrame(self.side_panel, fg_color="#f3f4f6", corner_radius=10)
        status_card.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(status_card, text="Drill Sequence:", font=ctk.CTkFont("Inter", 12)).pack(anchor="w", padx=15, pady=(15, 0))
        actions_text = " -> ".join(workflow_actions) if workflow_actions else "SAVDHAN"
        ctk.CTkLabel(
            status_card,
            text=actions_text,
            font=ctk.CTkFont("Inter", 14, "bold"),
            text_color="#059669",
            wraplength=250,
        ).pack(anchor="w", padx=15, pady=(0, 15))

        # Gauge container
        gauge_size = 120
        gauge_thickness = 12
        self.gauge_container = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        self.gauge_container.pack(fill="x", padx=20, pady=10)
        self.gauge_spine = CircularGauge(self.gauge_container, size=gauge_size, thickness=gauge_thickness, fg_color=ACCENT_GOLD, bg_color=CARD_COLOR)
        self.gauge_spine.pack(pady=8)
        self.gauge_heel = CircularGauge(self.gauge_container, size=gauge_size, thickness=gauge_thickness, fg_color=ACCENT_GOLD, bg_color=CARD_COLOR)
        self.gauge_heel.pack(pady=8)
        self.gauge_feet = CircularGauge(self.gauge_container, size=gauge_size, thickness=gauge_thickness, fg_color=ACCENT_GOLD, bg_color=CARD_COLOR)
        self.gauge_feet.pack(pady=8)
        self.gauge_hand = CircularGauge(self.gauge_container, size=gauge_size, thickness=gauge_thickness, fg_color=ACCENT_GOLD, bg_color=CARD_COLOR)
        self.gauge_hand.pack(pady=8)

        # Divider
        ctk.CTkFrame(self.side_panel, fg_color="#e5e7eb", height=2).pack(fill="x", padx=20, pady=20)

        # Action button
        self.record_btn = ctk.CTkButton(
            self.side_panel,
            text="START RECORDING",
            font=ctk.CTkFont("Inter", 14, "bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            corner_radius=8,
            height=45,
        )
        self.record_btn.pack(fill="x", padx=20, pady=10)

        # Layout weights for the two columns
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
