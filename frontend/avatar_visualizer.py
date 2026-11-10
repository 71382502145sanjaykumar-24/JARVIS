"""
JARVIS Holographic AI Avatar & HUD Animation Engine
Renders a glowing animated cybernetic avatar surrounded by rotating HUD targeting rings,
dynamic scanning radars, and reactive state auras.
"""

import math
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from pathlib import Path
from typing import Optional

from frontend.components import (
    COLOR_CYAN, 
    COLOR_ELECTRIC_BLUE, 
    COLOR_PANEL_BG, 
    COLOR_GREEN, 
    COLOR_RED
)

class HolographicAvatar(ctk.CTkFrame):
    """Futuristic animated holographic HUD avatar with rotating targeting arcs and pulse rings."""

    def __init__(self, master, avatar_path: str = "assets/jarvis_cyan.png", size: int = 220, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.size = size
        self.avatar_path = avatar_path
        
        # State tracking
        self.state = "IDLE"  # IDLE, LISTENING, PROCESSING, SPEAKING
        self.angle_outer = 0.0
        self.angle_inner = 180.0
        self.scan_y = 0.0
        self.scan_dir = 1.0
        self.pulse_phase = 0.0
        self._is_animating = False

        # Canvas for HUD and avatar
        self.canvas = tk.Canvas(
            self,
            width=self.size,
            height=self.size,
            bg=COLOR_PANEL_BG,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Prepare and cache masked avatar image
        self._load_avatar_image()

        # Start animation loop
        self.start_animation()

    def _load_avatar_image(self):
        """Creates a circular masked avatar with feathered edges."""
        try:
            raw_path = Path(self.avatar_path)
            if not raw_path.exists():
                self.tk_avatar = None
                return

            img = Image.open(raw_path).convert("RGBA")
            target_dim = int(self.size * 0.62)
            img = img.resize((target_dim, target_dim), Image.Resampling.LANCZOS)

            # Circular mask with antialiased edge
            mask = Image.new("L", (target_dim, target_dim), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((2, 2, target_dim - 2, target_dim - 2), fill=255)

            # Feather mask slightly
            img.putalpha(mask)
            self.tk_avatar = ImageTk.PhotoImage(img)
            self.avatar_dim = target_dim
        except Exception as e:
            print(f"Failed to load avatar image: {e}")
            self.tk_avatar = None

    def set_theme_avatar(self, new_path: str):
        """Swaps avatar image when theme changes."""
        self.avatar_path = new_path
        self._load_avatar_image()

    def set_state(self, new_state: str):
        """Updates animation state."""
        self.state = new_state

    def start_animation(self):
        if not self._is_animating:
            self._is_animating = True
            self._animate()

    def stop_animation(self):
        self._is_animating = False

    def _animate(self):
        if not self._is_animating:
            return

        self.canvas.delete("hud")

        cx = self.size / 2
        cy = self.size / 2
        
        # Determine speeds & colors by state
        if self.state == "LISTENING":
            rot_speed = 3.5
            hud_color = COLOR_GREEN
            secondary_color = COLOR_CYAN
            pulse_speed = 0.25
        elif self.state == "SPEAKING":
            rot_speed = 4.2
            hud_color = COLOR_CYAN
            secondary_color = COLOR_ELECTRIC_BLUE
            pulse_speed = 0.35
        elif self.state == "PROCESSING":
            rot_speed = 6.0
            hud_color = COLOR_ELECTRIC_BLUE
            secondary_color = "#38BDF8"
            pulse_speed = 0.20
        else: # IDLE
            rot_speed = 1.0
            hud_color = "#00D8F6"
            secondary_color = "#1E293B"
            pulse_speed = 0.08

        self.angle_outer = (self.angle_outer + rot_speed) % 360
        self.angle_inner = (self.angle_inner - rot_speed * 1.5) % 360
        self.pulse_phase += pulse_speed

        # 1. Pulsing Outer Aura Ring
        pulse_offset = math.sin(self.pulse_phase) * 4.0
        r_outer = (self.size / 2) - 8 + pulse_offset
        self.canvas.create_oval(
            cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
            outline=secondary_color,
            width=1,
            tags="hud"
        )

        # 2. Segmented Outer Rotating HUD Arcs
        r_arcs = (self.size / 2) - 14
        for offset_deg in [0, 90, 180, 270]:
            start_ang = (self.angle_outer + offset_deg) % 360
            self.canvas.create_arc(
                cx - r_arcs, cy - r_arcs, cx + r_arcs, cy + r_arcs,
                start=start_ang,
                extent=45,
                style="arc",
                outline=hud_color,
                width=2,
                tags="hud"
            )

        # 3. Inner Counter-Rotating Targeting Brackets
        r_inner = (self.size / 2) - 22
        for offset_deg in [30, 120, 210, 300]:
            start_ang = (self.angle_inner + offset_deg) % 360
            self.canvas.create_arc(
                cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner,
                start=start_ang,
                extent=25,
                style="arc",
                outline=hud_color if self.state != "IDLE" else "#0284C7",
                width=2,
                tags="hud"
            )

        # 4. Render Centered Masked Avatar
        if self.tk_avatar:
            self.canvas.create_image(cx, cy, image=self.tk_avatar, tags="hud")
        else:
            # Fallback glowing sphere
            self.canvas.create_oval(
                cx - 40, cy - 40, cx + 40, cy + 40,
                fill="#0F172A",
                outline=hud_color,
                width=2,
                tags="hud"
            )

        # 5. Holographic Scanning Line (sweeps up and down)
        avatar_r = (self.avatar_dim / 2) if self.tk_avatar else 40
        self.scan_y += self.scan_dir * (2.2 if self.state != "IDLE" else 1.2)
        if self.scan_y > avatar_r:
            self.scan_y = avatar_r
            self.scan_dir = -1.0
        elif self.scan_y < -avatar_r:
            self.scan_y = -avatar_r
            self.scan_dir = 1.0

        scan_curr_y = cy + self.scan_y
        line_w = math.sqrt(max(0, avatar_r**2 - self.scan_y**2)) * 0.95
        if line_w > 5:
            scan_color = COLOR_GREEN if self.state == "LISTENING" else COLOR_CYAN
            self.canvas.create_line(
                cx - line_w, scan_curr_y, cx + line_w, scan_curr_y,
                fill=scan_color,
                width=1,
                tags="hud"
            )

        # 6. Center Status Ring
        self.canvas.create_oval(
            cx - avatar_r - 2, cy - avatar_r - 2, cx + avatar_r + 2, cy + avatar_r + 2,
            outline=hud_color,
            width=2,
            tags="hud"
        )

        # Schedule next frame (approx 33 FPS)
        self.after(30, self._animate)

