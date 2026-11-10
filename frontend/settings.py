"""
JARVIS Settings Panel
Full configuration interface for AI, Voice, Automation, and App preferences.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable
from utils.config import config
from utils.logger import logger
from utils.permissions import permissions
from backend.ai_engine import ai_engine
from backend.voice_engine import voice_engine
from database.db_manager import db
from frontend.components import (
    GlassPanel, 
    GlowingButton, 
    COLOR_CYAN, 
    COLOR_ELECTRIC_BLUE, 
    COLOR_RED, 
    COLOR_GREEN, 
    COLOR_TEXT_PRIMARY, 
    COLOR_TEXT_MUTED
)

class SettingsView(ctk.CTkFrame):
    """Complete settings view with tabbed configuration panels."""

    def __init__(self, master, on_close: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, fg_color="#070B14", **kwargs)
        self.on_close = on_close

        self._build_header()
        self._build_tabs()

    def _build_header(self):
        """Header with title and close button."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(
            header,
            text="JARVIS SYSTEM CONFIGURATION",
            font=("Segoe UI", 16, "bold"),
            text_color=COLOR_CYAN
        )
        title.pack(side="left")

        if self.on_close:
            close_btn = ctk.CTkButton(
                header,
                text="✕ Back to Console",
                font=("Segoe UI", 11, "bold"),
                fg_color="#1E293B",
                hover_color="#334155",
                width=120,
                command=self.on_close
            )
            close_btn.pack(side="right")

    def _build_tabs(self):
        """Tabview containing AI, Voice, Automation, and System panels."""
        self.tabs = ctk.CTkTabview(
            self,
            fg_color="#0D1527",
            segmented_button_fg_color="#1E293B",
            segmented_button_selected_color=COLOR_CYAN,
            segmented_button_selected_hover_color="#00C2CF",
            segmented_button_unselected_hover_color="#334155",
            text_color="#070B14"
        )
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tab_ai = self.tabs.add("AI Intelligence")
        tab_voice = self.tabs.add("Voice & Audio")
        tab_auto = self.tabs.add("Automation & Safety")
        tab_app = self.tabs.add("System & Memory")

        self._populate_ai_tab(tab_ai)
        self._populate_voice_tab(tab_voice)
        self._populate_automation_tab(tab_auto)
        self._populate_system_tab(tab_app)

    # -------------------------------------------------------------------------
    # Tab 1: AI Intelligence
    # -------------------------------------------------------------------------
    def _populate_ai_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # API Key
        lbl_key = ctk.CTkLabel(scroll, text="OpenAI API Key:", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_PRIMARY)
        lbl_key.pack(anchor="w", pady=(5, 2))

        self.entry_key = ctk.CTkEntry(
            scroll, 
            placeholder_text="sk-...", 
            show="*", 
            width=450, 
            fg_color="#111A2E",
            border_color="#1E293B"
        )
        if config.openai_api_key:
            self.entry_key.insert(0, config.openai_api_key)
        self.entry_key.pack(anchor="w", pady=(0, 10))

        # Model Selection
        lbl_model = ctk.CTkLabel(scroll, text="GPT Model:", font=("Segoe UI", 12, "bold"), text_color=COLOR_TEXT_PRIMARY)
        lbl_model.pack(anchor="w", pady=(5, 2))

        self.model_combo = ctk.CTkComboBox(
            scroll,
            values=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            width=260,
            fg_color="#111A2E",
            border_color="#1E293B"
        )
        self.model_combo.set(config.openai_model)
        self.model_combo.pack(anchor="w", pady=(0, 15))

        # Test Connection Button & Status
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=5)

        test_btn = GlowingButton(
            btn_frame,
            text="Test Connection",
            variant="cyan",
            command=self._test_ai_connection
        )
        test_btn.pack(side="left", padx=(0, 10))

        save_ai_btn = GlowingButton(
            btn_frame,
            text="Save AI Settings",
            variant="blue",
            command=self._save_ai_settings
        )
        save_ai_btn.pack(side="left")

        self.lbl_ai_status = ctk.CTkLabel(
            scroll,
            text="",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_MUTED,
            wraplength=480
        )
        self.lbl_ai_status.pack(anchor="w", pady=10)

    def _test_ai_connection(self):
        self.lbl_ai_status.configure(text="Testing OpenAI API connection...", text_color=COLOR_CYAN)
        self.update_idletasks()
        
        # Temporarily use entered key
        old_key = config.openai_api_key
        config.openai_api_key = self.entry_key.get().strip()
        config.openai_model = self.model_combo.get().strip()
        
        status = ai_engine.test_connection()
        if status["success"]:
            self.lbl_ai_status.configure(text=f"✓ {status['message']}", text_color=COLOR_GREEN)
        else:
            self.lbl_ai_status.configure(text=f"✕ {status['message']}", text_color=COLOR_RED)

    def _save_ai_settings(self):
        new_key = self.entry_key.get().strip()
        new_model = self.model_combo.get().strip()
        config.update_and_persist(openai_api_key=new_key, openai_model=new_model)
        ai_engine.refresh_client()
        self.lbl_ai_status.configure(text="✓ AI settings saved successfully.", text_color=COLOR_GREEN)

    # -------------------------------------------------------------------------
    # Tab 2: Voice & Audio
    # -------------------------------------------------------------------------
    def _populate_voice_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Enable Speech Toggle
        self.speech_switch = ctk.CTkSwitch(
            scroll,
            text="Enable Voice Responses (Text-to-Speech)",
            font=("Segoe UI", 12, "bold"),
            progress_color=COLOR_CYAN
        )
        if config.speech_enabled:
            self.speech_switch.select()
        self.speech_switch.pack(anchor="w", pady=(5, 15))

        # Speed (Rate)
        lbl_rate = ctk.CTkLabel(scroll, text=f"Speech Rate (Speed): {config.voice_rate} WPM", font=("Segoe UI", 12))
        lbl_rate.pack(anchor="w")

        def on_rate_change(val):
            rate_int = int(val)
            lbl_rate.configure(text=f"Speech Rate (Speed): {rate_int} WPM")

        self.slider_rate = ctk.CTkSlider(
            scroll,
            from_=100,
            to=280,
            number_of_steps=18,
            progress_color=COLOR_CYAN,
            command=on_rate_change
        )
        self.slider_rate.set(config.voice_rate)
        self.slider_rate.pack(anchor="w", fill="x", pady=(5, 15))

        # Volume
        lbl_vol = ctk.CTkLabel(scroll, text=f"Volume: {int(config.voice_volume * 100)}%", font=("Segoe UI", 12))
        lbl_vol.pack(anchor="w")

        def on_vol_change(val):
            lbl_vol.configure(text=f"Volume: {int(val * 100)}%")

        self.slider_vol = ctk.CTkSlider(
            scroll,
            from_=0.1,
            to=1.0,
            number_of_steps=9,
            progress_color=COLOR_CYAN,
            command=on_vol_change
        )
        self.slider_vol.set(config.voice_volume)
        self.slider_vol.pack(anchor="w", fill="x", pady=(5, 15))

        # Test Voice Button
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=10)

        test_speech_btn = GlowingButton(
            btn_frame,
            text="Test Voice Sample",
            variant="cyan",
            command=self._test_speech
        )
        test_speech_btn.pack(side="left", padx=(0, 10))

        save_voice_btn = GlowingButton(
            btn_frame,
            text="Save Voice Settings",
            variant="blue",
            command=self._save_voice_settings
        )
        save_voice_btn.pack(side="left")

    def _test_speech(self):
        voice_engine.speak("JARVIS systems operational. Audio output online.")

    def _save_voice_settings(self):
        enabled = self.speech_switch.get() == 1
        rate = int(self.slider_rate.get())
        volume = float(self.slider_vol.get())
        config.update_and_persist(
            speech_enabled=enabled,
            voice_rate=rate,
            voice_volume=volume
        )
        voice_engine.set_rate(rate)
        voice_engine.set_volume(volume)

    # -------------------------------------------------------------------------
    # Tab 3: Automation & Safety
    # -------------------------------------------------------------------------
    def _populate_automation_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self.auto_switch = ctk.CTkSwitch(
            scroll,
            text="Enable Desktop Automation",
            font=("Segoe UI", 12, "bold"),
            progress_color=COLOR_CYAN
        )
        if config.automation_enabled:
            self.auto_switch.select()
        self.auto_switch.pack(anchor="w", pady=(5, 10))

        self.confirm_switch = ctk.CTkSwitch(
            scroll,
            text="Require Confirmation for Consequential Tasks",
            font=("Segoe UI", 12),
            progress_color=COLOR_CYAN
        )
        if config.require_confirmation:
            self.confirm_switch.select()
        self.confirm_switch.pack(anchor="w", pady=(5, 15))

        # Allowlist summary
        lbl_apps = ctk.CTkLabel(
            scroll,
            text=f"Approved Applications ({len(permissions.APPROVED_APPLICATIONS)} registered):",
            font=("Segoe UI", 12, "bold")
        )
        lbl_apps.pack(anchor="w", pady=(10, 4))

        app_list_str = ", ".join(list(permissions.APPROVED_APPLICATIONS.keys()))
        lbl_list = ctk.CTkLabel(
            scroll,
            text=app_list_str,
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_MUTED,
            wraplength=480,
            justify="left"
        )
        lbl_list.pack(anchor="w", pady=(0, 15))

        save_auto_btn = GlowingButton(
            scroll,
            text="Save Automation Policies",
            variant="blue",
            command=self._save_automation_settings
        )
        save_auto_btn.pack(anchor="w", pady=10)

    def _save_automation_settings(self):
        auto_enabled = self.auto_switch.get() == 1
        require_conf = self.confirm_switch.get() == 1
        config.update_and_persist(
            automation_enabled=auto_enabled,
            require_confirmation=require_conf
        )

    # -------------------------------------------------------------------------
    # Tab 4: System & Memory
    # -------------------------------------------------------------------------
    def _populate_system_tab(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_mem = ctk.CTkLabel(scroll, text="Conversation History & Memory:", font=("Segoe UI", 12, "bold"))
        lbl_mem.pack(anchor="w", pady=(5, 5))

        clear_btn = GlowingButton(
            scroll,
            text="Clear All Conversation History",
            variant="red",
            command=self._clear_history
        )
        clear_btn.pack(anchor="w", pady=(5, 15))

        self.lbl_hist_status = ctk.CTkLabel(scroll, text="", font=("Segoe UI", 11), text_color=COLOR_TEXT_MUTED)
        self.lbl_hist_status.pack(anchor="w", pady=5)

    def _clear_history(self):
        db.clear_all_conversations()
        self.lbl_hist_status.configure(text="✓ Conversation history cleared.", text_color=COLOR_GREEN)

