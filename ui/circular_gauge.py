# ui/circular_gauge.py
"""Reusable circular gauge widget for CustomTkinter.
Displays a percentage value as a colored arc with optional inner label.
Uses a CTkCanvas to draw the arc; supports dynamic updating via set_value().
"""
import customtkinter as ctk

class CircularGauge(ctk.CTkCanvas):
    def __init__(self, master, size=120, thickness=12, max_value=100, fg_color="#d4af37", bg_color="#1e293b", **kwargs):
        super().__init__(master, width=size, height=size, bg=bg_color, highlightthickness=0, **kwargs)
        self.size = size
        self.thickness = thickness
        self.max_value = max_value
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.arc = None
        self.text = None
        self._value = 0
        self.draw_gauge()

    def draw_gauge(self):
        # Clear existing items
        self.delete("all")
        # Background circle (full)
        self.create_oval(self.thickness/2, self.thickness/2, self.size-self.thickness/2, self.size-self.thickness/2, outline=self.bg_color, width=self.thickness)
        # Foreground arc representing value
        extent = 360 * (self._value / self.max_value)
        self.arc = self.create_arc(self.thickness/2, self.thickness/2, self.size-self.thickness/2, self.size-self.thickness/2,
                                   start=90, extent=-extent, style="arc", outline=self.fg_color, width=self.thickness)
        # Center text showing percentage
        perc = f"{int((self._value/self.max_value)*100)}%"
        self.text = self.create_text(self.size/2, self.size/2, text=perc, fill="#e2e8f0", font=("Inter", 14, "bold"))

    def set_value(self, value):
        """Update gauge to a new value (0‑max_value)."""
        if value < 0:
            value = 0
        if value > self.max_value:
            value = self.max_value
        self._value = value
        self.draw_gauge()
