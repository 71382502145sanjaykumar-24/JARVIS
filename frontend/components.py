"""
JARVIS Futuristic UI Components & Design Tokens
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable

# Cyberpunk / JARVIS Futuristic Color Palette
COLOR_BG_DARK = "#070B14"       # Deep Void Navy
COLOR_PANEL_BG = "#0D1527"      # Glassmorphism Navy Panel
COLOR_PANEL_BORDER = "#1E293B"  # Border Slate
COLOR_CYAN = "#00F0FF"          # Arc Reactor Cyan
COLOR_ELECTRIC_BLUE = "#0070F3" # Neon Electric Blue
COLOR_GREEN = "#00FFA3"         # Online Status Green
COLOR_RED = "#FF0055"           # Emergency / Error Red
COLOR_TEXT_PRIMARY = "#F8FAFC"  # High Contrast Text
COLOR_TEXT_MUTED = "#94A3B8"    # Subtitle / Details
COLOR_USER_BUBBLE = "#1E293B"   # User Chat Message Bubble
COLOR_AI_BUBBLE = "#0F213A"     # JARVIS Chat Message Bubble

class GlassPanel(ctk.CTkFrame):
    """Futuristic glass-styled container card with cyan-tinted borders."""
    def __init__(self, master, **kwargs):
        border_width = kwargs.pop("border_width", 1)
        border_color = kwargs.pop("border_color", COLOR_PANEL_BORDER)
        fg_color = kwargs.pop("fg_color", COLOR_PANEL_BG)
        corner_radius = kwargs.pop("corner_radius", 12)
        super().__init__(
            master,
            fg_color=fg_color,
            border_width=border_width,
            border_color=border_color,
            corner_radius=corner_radius,
            **kwargs
        )

class StatusPill(ctk.CTkFrame):
    """Small glowing status indicator pill."""
    def __init__(self, master, label: str, active: bool = False, active_color: str = COLOR_GREEN, **kwargs):
        super().__init__(master, fg_color="#0F172A", corner_radius=20, border_width=1, border_color="#334155", **kwargs)
        self.dot = ctk.CTkLabel(
            self, 
            text="●", 
            text_color=active_color if active else COLOR_TEXT_MUTED,
            font=("Segoe UI", 12, "bold")
        )
        self.dot.pack(side="left", padx=(10, 4), pady=4)
        
        self.lbl = ctk.CTkLabel(
            self, 
            text=label, 
            text_color=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold")
        )
        self.lbl.pack(side="left", padx=(0, 10), pady=4)

    def set_status(self, active: bool, text: Optional[str] = None, color: Optional[str] = None):
        """Updates indicator state."""
        dot_color = color or (COLOR_GREEN if active else COLOR_TEXT_MUTED)
        self.dot.configure(text_color=dot_color)
        if text:
            self.lbl.configure(text=text)

class GlowingButton(ctk.CTkButton):
    """Futuristic styled button with cyan/blue accents."""
    def __init__(self, master, text: str, command: Optional[Callable] = None, variant: str = "cyan", **kwargs):
        fg_color = COLOR_CYAN if variant == "cyan" else (COLOR_RED if variant == "red" else COLOR_ELECTRIC_BLUE)
        hover_color = "#00C2CF" if variant == "cyan" else ("#D90044" if variant == "red" else "#0056B3")
        text_color = "#070B14" if variant == "cyan" else "#FFFFFF"
        height = kwargs.pop("height", 36)
        corner_radius = kwargs.pop("corner_radius", 8)
        font = kwargs.pop("font", ("Segoe UI", 12, "bold"))
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=font,
            corner_radius=corner_radius,
            height=height,
            **kwargs
        )
