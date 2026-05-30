# ui/style.py
"""Central style definitions for the Drill application.
Provides color palette, fonts, and helper functions for glass‑morphism styling.
All UI modules should import from this file to ensure a consistent premium look.
"""

# Color palette (Indian military dignified dark navy with gold accents)
BG_COLOR = "#0f172a"            # Dark navy background
CARD_COLOR = "#1e293b"          # Slightly lighter for cards
ACCENT_BLUE = "#2563eb"         # Royal blue accent
ACCENT_GOLD = "#d4af37"         # Gold accent for icons and highlights
TEXT_PRIMARY = "#e2e8f0"        # Light gray for primary text
TEXT_SECONDARY = "#9ca3af"      # Medium gray for secondary text

# Font definitions – using Inter (should be installed via requirements or system)
INTER_REGULAR = ("Inter", 14)
INTER_SEMIBOLD = ("Inter", 14, "semibold")
INTER_BOLD = ("Inter", 14, "bold")

def apply_glass(frame, radius=20, blur=10, opacity=0.15):
    """Apply a simple glass‑morphism effect to a CustomTkinter frame.
    Args:
        frame: CTkFrame instance.
        radius: Corner radius.
        blur: Not directly supported – placeholder for future CSS‑like effect.
        opacity: Background opacity (0‑1). CustomTkinter does not support alpha in hex colors, so we use a solid card background to simulate a glass effect.
    """
    # Use a solid card-like background as a placeholder for glass‑morphism.
    frame.configure(corner_radius=radius, fg_color=CARD_COLOR)
