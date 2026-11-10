"""
JARVIS – Voice-Activated AI Virtual Assistant & Automation Tool
Master Entry Point
"""

import sys
import os
import signal
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from utils.logger import logger
from utils.config import config
from utils.helpers import ensure_tcl_tk_environment

# Ensure Tcl/Tk is located in virtual environments
ensure_tcl_tk_environment()

from database.db_manager import db
from backend.voice_engine import voice_engine
from backend.speech_recognition import speech_recognizer
from frontend.dashboard import JarvisDashboard

def handle_exit():
    """Performs clean shutdown of background workers and threads."""
    logger.info("Initiating JARVIS shutdown sequence...")
    try:
        voice_engine.stop()
        speech_recognizer.stop_listening()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    logger.info("JARVIS systems safely offline.")

def main():
    """Main application lifecycle runner."""
    logger.info("=" * 60)
    logger.info("Starting JARVIS AI Virtual Assistant & Automation Tool")
    logger.info(f"Root Directory: {BASE_DIR}")
    logger.info(f"OpenAI Key Configured: {config.has_valid_api_key()}")
    logger.info(f"Target OS: {sys.platform}")
    logger.info("=" * 60)

    try:
        app = JarvisDashboard()
        
        # Intercept window close event for clean shutdown
        def on_closing():
            handle_exit()
            app.destroy()
            sys.exit(0)

        app.protocol("WM_DELETE_WINDOW", on_closing)
        app.mainloop()

    except KeyboardInterrupt:
        handle_exit()
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error starting JARVIS: {e}", exc_info=True)
        print(f"Fatal error starting JARVIS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
