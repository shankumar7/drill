# Settings component for camera mapping

import customtkinter as ctk
import json
import os

from backend.calibration.interactive import get_camera_mapping, set_camera_mapping

class SettingsWindow(ctk.CTkToplevel):
    """A simple settings dialog to map front, back, and side cameras."""
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Camera Settings")
        self.geometry("300x250")
        self.resizable(False, False)

        # Load current mapping
        mapping = get_camera_mapping()

        # Dropdowns for each position
        ctk.CTkLabel(self, text="Front Camera Index:", anchor="w").pack(pady=(20, 5), fill="x", padx=20)
        self.front_var = ctk.IntVar(value=mapping.get("front", 0))
        self.front_dd = ctk.CTkComboBox(self, variable=self.front_var, values=[0, 1, 2, 3])
        self.front_dd.pack(pady=5, fill="x", padx=20)

        ctk.CTkLabel(self, text="Back Camera Index:", anchor="w").pack(pady=(10, 5), fill="x", padx=20)
        self.back_var = ctk.IntVar(value=mapping.get("back", 1))
        self.back_dd = ctk.CTkComboBox(self, variable=self.back_var, values=[0, 1, 2, 3])
        self.back_dd.pack(pady=5, fill="x", padx=20)

        ctk.CTkLabel(self, text="Side Camera Index:", anchor="w").pack(pady=(10, 5), fill="x", padx=20)
        self.side_var = ctk.IntVar(value=mapping.get("side", 2))
        self.side_dd = ctk.CTkComboBox(self, variable=self.side_var, values=[0, 1, 2, 3])
        self.side_dd.pack(pady=5, fill="x", padx=20)

        # Save button
        ctk.CTkButton(self, text="Save", command=self.save).pack(pady=20)

    def save(self):
        set_camera_mapping(self.front_var.get(), self.back_var.get(), self.side_var.get())
        self.destroy()
