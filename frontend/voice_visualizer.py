"""
JARVIS Voice Waveform & Arc Reactor Visualizer
Renders dynamic waveforms and pulsing arc-reactor rings based on assistant state.
"""

import math
import time
import tkinter as tk
import customtkinter as ctk
from typing import Optional
from frontend.components import COLOR_CYAN, COLOR_ELECTRIC_BLUE, COLOR_PANEL_BG, COLOR_RED, COLOR_GREEN

class VoiceVisualizer(ctk.CTkFrame):
    """Futuristic animated audio visualizer with multi-harmonic frequency waves."""

    STATE_IDLE = "IDLE"
    STATE_LISTENING = "LISTENING"
    STATE_PROCESSING = "PROCESSING"
    STATE_SPEAKING = "SPEAKING"

    def __init__(self, master, width: int = 500, height: int = 100, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.width = width
        self.height = height
        self.state = self.STATE_IDLE
        self.phase = 0.0
        self._is_animating = False

        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg=COLOR_PANEL_BG,
            highlightthickness=1,
            highlightbackground="#1E293B"
        )
        self.canvas.pack(fill="both", expand=True)

        self.start_animation()

    def set_state(self, new_state: str):
        """Sets the visualizer state to update animation dynamics and colors."""
        self.state = new_state

    def start_animation(self):
        """Starts the animation loop."""
        if not self._is_animating:
            self._is_animating = True
            self._animate_frame()

    def stop_animation(self):
        """Halts the animation loop."""
        self._is_animating = False

    def _animate_frame(self):
        """Draws one frame of the dynamic waveform."""
        if not self._is_animating:
            return

        self.canvas.delete("wave")
        self.canvas.delete("text")
        
        mid_y = self.height / 2
        w = self.canvas.winfo_width() or self.width
        h = self.canvas.winfo_height() or self.height
        mid_y = h / 2

        # Parameters based on current state
        if self.state == self.STATE_LISTENING:
            amplitude = 25.0
            speed = 0.15
            color = COLOR_GREEN
            status_text = "● LISTENING..."
        elif self.state == self.STATE_SPEAKING:
            amplitude = 30.0
            speed = 0.22
            color = COLOR_CYAN
            status_text = "● SPEAKING..."
        elif self.state == self.STATE_PROCESSING:
            amplitude = 12.0
            speed = 0.28
            color = COLOR_ELECTRIC_BLUE
            status_text = "● PROCESSING INTENT..."
        else: # IDLE
            amplitude = 4.0
            speed = 0.05
            color = "#334155"
            status_text = "● READY (STANDBY)"

        self.phase += speed

        # Draw ambient center status text
        self.canvas.create_text(
            w / 2, 
            16, 
            text=status_text, 
            fill=color, 
            font=("Segoe UI", 9, "bold"),
            tags="text"
        )

        # Draw multi-harmonic wave lines
        for harmonic, alpha_color, width in [
            (1.0, color, 2),
            (1.8, COLOR_ELECTRIC_BLUE if self.state != self.STATE_IDLE else "#1E293B", 1),
            (0.5, "#00FFA3" if self.state == self.STATE_SPEAKING else color, 1)
        ]:
            points = []
            steps = 40
            dx = w / steps
            for i in range(steps + 1):
                x = i * dx
                # Normalizing bell curve envelope so wave tapers off at the borders
                norm_x = (x / w) * 2 - 1 # -1 to 1
                envelope = math.exp(-2.5 * (norm_x ** 2))
                y = mid_y + math.sin(i * 0.3 * harmonic + self.phase) * amplitude * envelope
                points.extend([x, y])

            if len(points) >= 4:
                self.canvas.create_line(
                    points, 
                    fill=alpha_color, 
                    width=width, 
                    smooth=True, 
                    tags="wave"
                )

        # Schedule next frame (approx 30-40 FPS)
        self.after(30, self._animate_frame)

