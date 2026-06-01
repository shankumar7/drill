"""ui/components/navigation_bar.py

Implements a top navigation bar for the Drill application.
All buttons are placeholders that can be wired to real actions later.
Uses the shared style constants from `ui.style` for colors and fonts.
"""

import customtkinter as ctk
from ui.style import BG_COLOR, ACCENT_GOLD, INTER_BOLD

class NavigationBar(ctk.CTkFrame):
    """A horizontal navigation bar with placeholder buttons.
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, fg_color=BG_COLOR, *args, **kwargs)
        # Example navigation buttons
        self.home_btn = ctk.CTkButton(self, text="Home",
                                      font=INTER_BOLD,
                                      fg_color=ACCENT_GOLD,
                                      hover_color=ACCENT_GOLD)
        self.home_btn.pack(side="left", padx=10, pady=5)
        self.settings_btn = ctk.CTkButton(self, text="Settings",
                                          font=INTER_BOLD,
                                          fg_color=ACCENT_GOLD,
                                          hover_color=ACCENT_GOLD)
        self.settings_btn.pack(side="left", padx=10, pady=5)
        self.help_btn = ctk.CTkButton(self, text="Help",
                                      font=INTER_BOLD,
                                      fg_color=ACCENT_GOLD,
                                      hover_color=ACCENT_GOLD)
        self.help_btn.pack(side="left", padx=10, pady=5)
