"""ui/components/header.py

Header component for the Drill application.
Displays a title and a theme toggle button (light/dark).
Uses shared style constants for colors and fonts.
"""

import customtkinter as ctk
from ui.style import BG_COLOR, ACCENT_GOLD, INTER_BOLD, INTER_REGULAR

class Header(ctk.CTkFrame):
    """Header with app title and a theme toggle."""
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color=BG_COLOR, *args, **kwargs)
        # Title label
        self.title_label = ctk.CTkLabel(
            self,
            text="Military Drill Analysis",
            font=INTER_BOLD,
            text_color=ACCENT_GOLD,
        )
        self.title_label.pack(side="left", padx=10, pady=5)
        # Theme toggle button
        self.toggle_btn = ctk.CTkButton(
            self,
            text="Toggle Theme",
            font=INTER_REGULAR,
            fg_color=ACCENT_GOLD,
            hover_color=ACCENT_GOLD,
            command=self.toggle_theme,
        )
        self.toggle_btn.pack(side="right", padx=10, pady=5)

    def toggle_theme(self):
        # Simple toggle between light and dark appearance modes
        current = ctk.get_appearance_mode()
        new_mode = "dark" if current == "light" else "light"
        ctk.set_appearance_mode(new_mode)
