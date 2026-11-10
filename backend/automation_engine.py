"""
JARVIS Desktop Automation Engine
Provides controlled, permission-checked keyboard and mouse automation via PyAutoGUI.
"""

import time
import threading
from typing import Dict, Any, Optional, Callable
import pyautogui
from utils.logger import logger
from utils.permissions import permissions
from utils.config import config
from database.db_manager import db

# Enable PyAutoGUI fail-safe (moving cursor to corner stops action)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

class AutomationEngine:
    """Safely executes keyboard and mouse tasks with confirmation checks and emergency halts."""

    def __init__(self):
        self.confirmation_callback: Optional[Callable[[str], bool]] = None
        self.status_callback: Optional[Callable[[bool, str], None]] = None

    def _notify_status(self, is_active: bool, description: str = ""):
        """Notifies UI whether an automation task is active."""
        permissions.is_automation_active = is_active
        if self.status_callback:
            try:
                self.status_callback(is_active, description)
            except Exception as e:
                logger.error(f"Error in automation status callback: {e}")

    def type_text(self, text: str, delay: float = 0.05) -> Dict[str, Any]:
        """Types text using keyboard emulation after safety verification."""
        if not config.automation_enabled:
            return {"success": False, "message": "Desktop automation is disabled in settings."}

        if permissions.is_stopped:
            return {"success": False, "message": "Automation aborted by emergency stop."}

        # Consequential action verification
        if permissions.requires_confirmation(text) or config.require_confirmation:
            if self.confirmation_callback:
                approved = self.confirmation_callback(f"Authorize typing: '{text[:40]}...'?")
                if not approved:
                    msg = "Typing action canceled by user."
                    db.log_automation("type_text", text[:50], "denied", msg)
                    return {"success": False, "message": msg}

        try:
            self._notify_status(True, f"Typing text...")
            time.sleep(1.0) # Brief delay to allow target window focus
            
            if permissions.is_stopped:
                return {"success": False, "message": "Emergency stop triggered."}

            pyautogui.write(text, interval=delay)
            msg = f"Typed requested text successfully."
            db.log_automation("type_text", text[:50], "success", msg)
            return {"success": True, "message": msg}
        except Exception as e:
            msg = f"Automation error while typing: {e}"
            logger.error(msg)
            db.log_automation("type_text", text[:50], "error", msg)
            return {"success": False, "message": msg}
        finally:
            self._notify_status(False)

    def press_key(self, key_name: str) -> Dict[str, Any]:
        """Presses a single key or key combo (e.g. 'enter', 'tab', 'ctrl+s')."""
        if not config.automation_enabled:
            return {"success": False, "message": "Desktop automation is disabled."}

        if permissions.is_stopped:
            return {"success": False, "message": "Automation stopped."}

        try:
            self._notify_status(True, f"Pressing key: {key_name}")
            keys = [k.strip().lower() for k in key_name.split("+")]
            if len(keys) == 1:
                pyautogui.press(keys[0])
            else:
                pyautogui.hotkey(*keys)
            
            msg = f"Pressed key '{key_name}'."
            db.log_automation("press_key", key_name, "success", msg)
            return {"success": True, "message": msg}
        except Exception as e:
            msg = f"Key press failed: {e}"
            logger.error(msg)
            db.log_automation("press_key", key_name, "error", msg)
            return {"success": False, "message": msg}
        finally:
            self._notify_status(False)

    def scroll_page(self, clicks: int = -500) -> Dict[str, Any]:
        """Scrolls the active window up (positive) or down (negative)."""
        if not config.automation_enabled or permissions.is_stopped:
            return {"success": False, "message": "Automation disabled or stopped."}

        try:
            self._notify_status(True, "Scrolling window...")
            pyautogui.scroll(clicks)
            direction = "down" if clicks < 0 else "up"
            msg = f"Scrolled {direction}."
            db.log_automation("scroll", str(clicks), "success", msg)
            return {"success": True, "message": msg}
        except Exception as e:
            msg = f"Scroll failed: {e}"
            logger.error(msg)
            return {"success": False, "message": msg}
        finally:
            self._notify_status(False)

    def emergency_stop(self):
        """Immediately halts all automation and sets safety flag."""
        permissions.trigger_emergency_stop()
        self._notify_status(False, "EMERGENCY STOP")
        logger.warning("Emergency stop triggered on Automation Engine.")


# Global automation engine instance
automation_engine = AutomationEngine()

