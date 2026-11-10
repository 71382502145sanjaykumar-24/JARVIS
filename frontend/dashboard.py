"""
JARVIS Futuristic Desktop Dashboard
Main HUD integrating Voice Recognition, AI Conversation, Real-time Visualizer, System Telemetry, and Automation.
"""

import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional

from utils.logger import logger
from utils.config import config
from utils.helpers import get_system_metrics, get_current_time_str, ensure_tcl_tk_environment

# Ensure Tcl/Tk is located in virtual environments
ensure_tcl_tk_environment()

from database.db_manager import db
from backend.voice_engine import voice_engine
from backend.speech_recognition import speech_recognizer
from backend.command_processor import command_processor
from backend.automation_engine import automation_engine

from frontend.components import (
    GlassPanel, 
    StatusPill, 
    GlowingButton,
    COLOR_BG_DARK, 
    COLOR_PANEL_BG, 
    COLOR_CYAN, 
    COLOR_ELECTRIC_BLUE, 
    COLOR_GREEN, 
    COLOR_RED, 
    COLOR_TEXT_PRIMARY, 
    COLOR_TEXT_MUTED
)
from frontend.voice_visualizer import VoiceVisualizer
from frontend.chat_interface import ChatInterface
from frontend.settings import SettingsView

# Set CustomTkinter defaults
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JarvisDashboard(ctk.CTk):
    """Main Application Window for JARVIS AI Virtual Assistant."""

    def __init__(self):
        super().__init__()
        
        self.title("JARVIS — Voice-Activated AI Virtual Assistant & Automation Tool")
        self.geometry("1100x740")
        self.minsize(950, 650)
        self.configure(fg_color=COLOR_BG_DARK)

        # State tracking
        self.current_conversation_id = db.create_conversation("Main Session")
        self.is_processing = False

        # Hook safety callbacks
        automation_engine.confirmation_callback = self._prompt_confirmation
        automation_engine.status_callback = self._on_automation_status

        # Build UI layout
        self._build_top_hud()
        self._build_body()
        self._build_bottom_command_bar()

        # Connect voice callbacks
        self._setup_voice_engine_hooks()

        # Start background telemetry update loop
        self._update_telemetry()

        # Welcome message
        self.after(400, self._show_welcome_message)

    def _build_top_hud(self):
        """Top bar displaying JARVIS Title, Telemetry Pills, Emergency Stop, and Settings."""
        self.top_bar = GlassPanel(self, height=60, corner_radius=0, border_width=0, border_color="#1E293B")
        self.top_bar.pack(fill="x", side="top", padx=0, pady=0)

        # Title branding
        title_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=10)

        logo_lbl = ctk.CTkLabel(
            title_frame, 
            text="◈ J.A.R.V.I.S.", 
            font=("Segoe UI", 18, "bold"), 
            text_color=COLOR_CYAN
        )
        logo_lbl.pack(side="left")

        ver_lbl = ctk.CTkLabel(
            title_frame, 
            text="AI ASSISTANT v2.0", 
            font=("Segoe UI", 10), 
            text_color=COLOR_TEXT_MUTED
        )
        ver_lbl.pack(side="left", padx=(8, 0), pady=(3, 0))

        # Right side action controls
        right_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=10)

        # Status Indicators
        self.pill_ai = StatusPill(
            right_frame, 
            label="AI ONLINE" if config.has_valid_api_key() else "AI LOCAL", 
            active=config.has_valid_api_key()
        )
        self.pill_ai.pack(side="left", padx=5)

        self.pill_mic = StatusPill(
            right_frame, 
            label="MIC READY", 
            active=True, 
            active_color=COLOR_CYAN
        )
        self.pill_mic.pack(side="left", padx=5)

        # Emergency Stop Button
        self.btn_emergency = GlowingButton(
            right_frame,
            text="🛑 EMERGENCY STOP",
            variant="red",
            command=self._emergency_stop_clicked,
            width=140,
            height=32
        )
        self.btn_emergency.pack(side="left", padx=8)

        # Settings Button
        self.btn_settings = ctk.CTkButton(
            right_frame,
            text="⚙ SETTINGS",
            font=("Segoe UI", 11, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            width=100,
            height=32,
            command=self._toggle_settings
        )
        self.btn_settings.pack(side="left", padx=5)

    def _build_body(self):
        """Central layout consisting of Left Side Telemetry/Visualizer and Right Side Chat."""
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # LEFT HUD PANEL (Telemetry, Visualizer, Quick Chips)
        self.left_panel = GlassPanel(self.body_frame, width=380)
        self.left_panel.pack(side="left", fill="both", padx=(0, 10))

        # Core Arc Visualizer
        lbl_vis = ctk.CTkLabel(
            self.left_panel, 
            text="VOICE SYNTHESIS & SPECTRUM", 
            font=("Segoe UI", 11, "bold"), 
            text_color=COLOR_CYAN
        )
        lbl_vis.pack(anchor="w", padx=16, pady=(16, 6))

        self.visualizer = VoiceVisualizer(self.left_panel, height=90)
        self.visualizer.pack(fill="x", padx=16, pady=(0, 12))

        # Central Mic Activation Orb
        orb_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        orb_frame.pack(fill="x", padx=16, pady=8)

        self.btn_mic_activate = GlowingButton(
            orb_frame,
            text="🎙 ACTIVATE VOICE (PUSH TO TALK)",
            variant="cyan",
            height=44,
            command=self._toggle_microphone
        )
        self.btn_mic_activate.pack(fill="x")

        # Telemetry Metrics Card
        lbl_diag = ctk.CTkLabel(
            self.left_panel, 
            text="SYSTEM TELEMETRY", 
            font=("Segoe UI", 11, "bold"), 
            text_color=COLOR_CYAN
        )
        lbl_diag.pack(anchor="w", padx=16, pady=(16, 4))

        self.diag_card = ctk.CTkFrame(self.left_panel, fg_color="#070B14", corner_radius=8, border_width=1, border_color="#1E293B")
        self.diag_card.pack(fill="x", padx=16, pady=(0, 10))

        self.lbl_cpu = ctk.CTkLabel(self.diag_card, text="CPU: 0%", font=("Segoe UI", 11), text_color=COLOR_TEXT_PRIMARY)
        self.lbl_cpu.pack(anchor="w", padx=12, pady=(8, 2))

        self.lbl_ram = ctk.CTkLabel(self.diag_card, text="RAM: 0 / 0 GB", font=("Segoe UI", 11), text_color=COLOR_TEXT_PRIMARY)
        self.lbl_ram.pack(anchor="w", padx=12, pady=2)

        self.lbl_time = ctk.CTkLabel(self.diag_card, text="TIME: --:--", font=("Segoe UI", 11), text_color=COLOR_CYAN)
        self.lbl_time.pack(anchor="w", padx=12, pady=(2, 8))

        # Quick Voice Command Shortcuts
        lbl_shortcuts = ctk.CTkLabel(
            self.left_panel, 
            text="QUICK COMMAND SHORTCUTS", 
            font=("Segoe UI", 11, "bold"), 
            text_color=COLOR_CYAN
        )
        lbl_shortcuts.pack(anchor="w", padx=16, pady=(12, 6))

        shortcuts = [
            ("Open Notepad", "Open Notepad"),
            ("Open YouTube", "Open YouTube"),
            ("Search AI News", "Search artificial intelligence news"),
            ("System Health", "System status"),
            ("What time is it?", "What time is it?"),
        ]

        for label_text, cmd_text in shortcuts:
            btn = ctk.CTkButton(
                self.left_panel,
                text=f"› {label_text}",
                font=("Segoe UI", 11),
                fg_color="#111A2E",
                hover_color="#1E293B",
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
                height=28,
                command=lambda c=cmd_text: self._execute_user_command(c)
            )
            btn.pack(fill="x", padx=16, pady=2)

        # RIGHT PANEL (Interactive Chat Interface)
        self.right_panel = GlassPanel(self.body_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)

        chat_header = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        chat_header.pack(fill="x", padx=16, pady=(12, 6))

        chat_title = ctk.CTkLabel(
            chat_header, 
            text="NEURAL CONVERSATION STREAM", 
            font=("Segoe UI", 12, "bold"), 
            text_color=COLOR_CYAN
        )
        chat_title.pack(side="left")

        clear_chat_btn = ctk.CTkButton(
            chat_header,
            text="Clear Stream",
            font=("Segoe UI", 10),
            fg_color="transparent",
            hover_color="#1E293B",
            text_color=COLOR_TEXT_MUTED,
            width=70,
            command=self._clear_chat_stream
        )
        clear_chat_btn.pack(side="right")

        self.chat_view = ChatInterface(self.right_panel)
        self.chat_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_bottom_command_bar(self):
        """Bottom bar with user text entry, Submit, Voice trigger, and live automation banner."""
        self.bottom_bar = GlassPanel(self, height=70, corner_radius=0, border_width=0)
        self.bottom_bar.pack(fill="x", side="bottom")

        inner_frame = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        inner_frame.pack(fill="x", padx=20, pady=12)

        # Command Text Input
        self.cmd_entry = ctk.CTkEntry(
            inner_frame,
            placeholder_text="Enter a command or ask JARVIS anything... (e.g. 'Open Notepad', 'Search Python', 'Explain AI')",
            font=("Segoe UI", 12),
            fg_color="#0A0F1D",
            border_color="#1E293B",
            height=42
        )
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.cmd_entry.bind("<Return>", lambda event: self._on_submit_typed_command())

        # Send Button
        self.btn_send = GlowingButton(
            inner_frame,
            text="TRANSMIT",
            variant="blue",
            width=110,
            height=42,
            command=self._on_submit_typed_command
        )
        self.btn_send.pack(side="left")

    # -------------------------------------------------------------------------
    # Setup Voice Hooks & Threading
    # -------------------------------------------------------------------------
    def _setup_voice_engine_hooks(self):
        """Connects voice engine and speech recognizer callbacks to UI updates."""
        voice_engine.on_start_speaking = lambda: self._safe_ui_call(
            lambda: self.visualizer.set_state(VoiceVisualizer.STATE_SPEAKING)
        )
        voice_engine.on_stop_speaking = lambda: self._safe_ui_call(
            lambda: self.visualizer.set_state(VoiceVisualizer.STATE_IDLE)
        )

        speech_recognizer.on_start_listening = lambda: self._safe_ui_call(self._on_mic_start)
        speech_recognizer.on_stop_listening = lambda: self._safe_ui_call(self._on_mic_stop)
        speech_recognizer.on_recognized = lambda text: self._safe_ui_call(
            lambda: self._execute_user_command(text)
        )
        speech_recognizer.on_error = lambda err: self._safe_ui_call(
            lambda: self._on_speech_error(err)
        )

    def _safe_ui_call(self, func):
        """Ensures function executes on the Tkinter main UI thread."""
        try:
            self.after(0, func)
        except Exception as e:
            logger.error(f"Error invoking safe UI call: {e}")

    def _show_welcome_message(self):
        """Greets user and displays initial instructions."""
        welcome_text = (
            "Good day, sir. JARVIS is fully initialized and operational. "
            "You can speak via the microphone button or type commands below. "
            "How may I assist you today?"
        )
        self.chat_view.add_message("jarvis", welcome_text, intent="greeting")
        voice_engine.speak("Good day. JARVIS is initialized and operational.")

    # -------------------------------------------------------------------------
    # Microphone & Command Execution
    # -------------------------------------------------------------------------
    def _toggle_microphone(self):
        """Activates speech recognition in a background thread."""
        if speech_recognizer.is_listening:
            speech_recognizer.stop_listening()
        else:
            speech_recognizer.listen_once_async()

    def _on_mic_start(self):
        self.pill_mic.set_status(True, "LISTENING...", COLOR_GREEN)
        self.btn_mic_activate.configure(text="🔴 LISTENING... (SPEAK NOW)", fg_color=COLOR_RED)
        self.visualizer.set_state(VoiceVisualizer.STATE_LISTENING)

    def _on_mic_stop(self):
        self.pill_mic.set_status(True, "MIC READY", COLOR_CYAN)
        self.btn_mic_activate.configure(text="🎙 ACTIVATE VOICE (PUSH TO TALK)", fg_color=COLOR_CYAN)
        if not voice_engine.is_speaking and not self.is_processing:
            self.visualizer.set_state(VoiceVisualizer.STATE_IDLE)

    def _on_speech_error(self, error_message: str):
        self.chat_view.add_message("jarvis", f"Audio input notice: {error_message}", intent="speech_notice")
        self.visualizer.set_state(VoiceVisualizer.STATE_IDLE)

    def _on_submit_typed_command(self):
        text = self.cmd_entry.get().strip()
        if not text:
            return
        self.cmd_entry.delete(0, "end")
        self._execute_user_command(text)

    def _execute_user_command(self, command_text: str):
        """Executes a command asynchronously without blocking the UI."""
        if not command_text or not command_text.strip():
            return

        self.chat_view.add_message("user", command_text)
        self.visualizer.set_state(VoiceVisualizer.STATE_PROCESSING)
        self.is_processing = True

        # Run processing on a background worker thread
        threading.Thread(
            target=self._worker_process_command, 
            args=(command_text,), 
            daemon=True
        ).start()

    def _worker_process_command(self, command_text: str):
        """Worker thread for command execution."""
        try:
            result = command_processor.process(command_text, conversation_id=self.current_conversation_id)
            response_text = result.get("response", "")
            intent = result.get("intent", "general")

            # Post response to UI thread
            self._safe_ui_call(lambda: self._handle_command_completed(response_text, intent))
            
            # Speak response if speech is enabled
            if response_text and intent != "stop_speech":
                voice_engine.speak(response_text)
        except Exception as e:
            logger.error(f"Error during command execution: {e}")
            err_msg = f"An error occurred while executing command: {str(e)}"
            self._safe_ui_call(lambda: self._handle_command_completed(err_msg, "error"))
        finally:
            self.is_processing = False

    def _handle_command_completed(self, response_text: str, intent: str):
        if response_text:
            self.chat_view.add_message("jarvis", response_text, intent=intent)
        if not voice_engine.is_speaking:
            self.visualizer.set_state(VoiceVisualizer.STATE_IDLE)

    # -------------------------------------------------------------------------
    # Safety Controls & Telemetry
    # -------------------------------------------------------------------------
    def _prompt_confirmation(self, action_description: str) -> bool:
        """Modal prompt asking user to confirm potentially consequential automation."""
        return messagebox.askyesno(
            "JARVIS Automation Authorization",
            f"JARVIS requests authorization to perform desktop action:\n\n{action_description}\n\nDo you authorize this action?",
            parent=self
        )

    def _on_automation_status(self, is_active: bool, description: str = ""):
        """Updates UI status pill when automation is actively running."""
        pass

    def _emergency_stop_clicked(self):
        """Immediate full stop of automation and speech."""
        automation_engine.emergency_stop()
        voice_engine.stop()
        speech_recognizer.stop_listening()
        self.visualizer.set_state(VoiceVisualizer.STATE_IDLE)
        self.chat_view.add_message("jarvis", "🛑 EMERGENCY STOP EXECUTED. All automations and voice speech halted.", intent="emergency_stop")

    def _clear_chat_stream(self):
        self.chat_view.clear()
        self.chat_view.add_message("jarvis", "Neural stream cleared.", intent="system")

    def _toggle_settings(self):
        """Displays or hides the modal settings view."""
        if hasattr(self, "settings_view") and self.settings_view.winfo_ismapped():
            self.settings_view.destroy()
            return

        self.settings_view = SettingsView(self, on_close=lambda: self.settings_view.destroy())
        self.settings_view.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

    def _update_telemetry(self):
        """Polls system metrics every 3 seconds to keep HUD live."""
        try:
            metrics = get_system_metrics()
            self.lbl_cpu.configure(text=f"CPU: {metrics['cpu_percent']}%")
            self.lbl_ram.configure(text=f"RAM: {metrics['ram_used_gb']} / {metrics['ram_total_gb']} GB ({metrics['ram_percent']}%)")
            self.lbl_time.configure(text=f"TIME: {get_current_time_str()}")
            
            # Update AI pill status dynamically
            if config.has_valid_api_key():
                self.pill_ai.set_status(True, "AI ONLINE", COLOR_GREEN)
            else:
                self.pill_ai.set_status(False, "AI LOCAL", COLOR_CYAN)
        except Exception as e:
            logger.warning(f"Error updating telemetry: {e}")

        self.after(3000, self._update_telemetry)
