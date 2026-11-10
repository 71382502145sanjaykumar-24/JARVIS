"""
JARVIS Chat Interface
Scrollable conversation window displaying user queries and assistant responses with timestamps and intent tags.
"""

import customtkinter as ctk
import datetime
from typing import Optional
from frontend.components import (
    COLOR_CYAN, 
    COLOR_ELECTRIC_BLUE, 
    COLOR_TEXT_PRIMARY, 
    COLOR_TEXT_MUTED, 
    COLOR_USER_BUBBLE, 
    COLOR_AI_BUBBLE
)

class ChatMessageBubble(ctk.CTkFrame):
    """Visual bubble card representing a single conversation turn."""

    def __init__(self, master, sender: str, text: str, timestamp: Optional[str] = None, intent: Optional[str] = None, **kwargs):
        is_user = sender.lower() == "user"
        bg_color = COLOR_USER_BUBBLE if is_user else COLOR_AI_BUBBLE
        border_color = "#334155" if is_user else "#0284C7"
        
        super().__init__(
            master, 
            fg_color=bg_color, 
            corner_radius=12, 
            border_width=1, 
            border_color=border_color, 
            **kwargs
        )

        time_label = timestamp or datetime.datetime.now().strftime("%I:%M %p")
        sender_title = "YOU" if is_user else "JARVIS"
        title_color = "#94A3B8" if is_user else COLOR_CYAN

        # Header bar
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(8, 2))

        sender_lbl = ctk.CTkLabel(
            header_frame, 
            text=sender_title, 
            text_color=title_color, 
            font=("Segoe UI", 10, "bold")
        )
        sender_lbl.pack(side="left")

        if intent and not is_user:
            badge = ctk.CTkLabel(
                header_frame,
                text=f"[{intent.upper()}]",
                text_color=COLOR_ELECTRIC_BLUE,
                font=("Segoe UI", 9)
            )
            badge.pack(side="left", padx=6)

        time_lbl = ctk.CTkLabel(
            header_frame, 
            text=time_label, 
            text_color=COLOR_TEXT_MUTED, 
            font=("Segoe UI", 9)
        )
        time_lbl.pack(side="right")

        # Message body
        msg_lbl = ctk.CTkLabel(
            self,
            text=text,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 12),
            wraplength=520,
            justify="left",
            anchor="w"
        )
        msg_lbl.pack(fill="x", padx=12, pady=(2, 10))


class ChatInterface(ctk.CTkScrollableFrame):
    """Scrollable container of chat messages."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master, 
            fg_color="transparent", 
            corner_radius=0, 
            **kwargs
        )

    def add_message(self, sender: str, text: str, intent: Optional[str] = None):
        """Appends a new message bubble and scrolls to bottom."""
        bubble = ChatMessageBubble(self, sender=sender, text=text, intent=intent)
        
        # User messages right-aligned, JARVIS left-aligned
        is_user = sender.lower() == "user"
        padx_tuple = (60, 10) if is_user else (10, 60)
        bubble.pack(fill="x", padx=padx_tuple, pady=6)

        # Force scroll to bottom
        self.after(50, lambda: self._parent_canvas.yview_moveto(1.0))

    def clear(self):
        """Clears all displayed chat bubbles."""
        for widget in self.winfo_children():
            widget.destroy()

