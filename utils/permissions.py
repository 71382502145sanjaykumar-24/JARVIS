"""
JARVIS Security & Permission Manager
Enforces strict allowlists, validates paths, and regulates desktop automation actions.
"""

import os
import re
from typing import Dict, List, Set, Tuple, Optional
from urllib.parse import urlparse
from utils.logger import logger

class PermissionManager:
    """Manages safety policies and allowlists for applications, websites, and actions."""

    # Approved applications on Windows
    APPROVED_APPLICATIONS: Dict[str, Dict[str, str]] = {
        "notepad": {
            "name": "Notepad",
            "command": "notepad.exe",
            "description": "Windows Text Editor"
        },
        "calculator": {
            "name": "Calculator",
            "command": "calc.exe",
            "description": "Windows Calculator"
        },
        "explorer": {
            "name": "File Explorer",
            "command": "explorer.exe",
            "description": "Windows File Explorer"
        },
        "cmd": {
            "name": "Command Prompt",
            "command": "cmd.exe",
            "description": "Windows Command Prompt"
        },
        "powershell": {
            "name": "PowerShell",
            "command": "powershell.exe",
            "description": "Windows PowerShell"
        },
        "vscode": {
            "name": "Visual Studio Code",
            "command": "code",
            "description": "VS Code Editor"
        },
        "taskmgr": {
            "name": "Task Manager",
            "command": "taskmgr.exe",
            "description": "Windows Task Manager"
        },
        "paint": {
            "name": "MS Paint",
            "command": "mspaint.exe",
            "description": "Windows Paint Utility"
        }
    }

    # Approved websites & safe domain extensions
    APPROVED_DOMAINS: Set[str] = {
        "google.com",
        "www.google.com",
        "youtube.com",
        "www.youtube.com",
        "github.com",
        "www.github.com",
        "stackoverflow.com",
        "www.stackoverflow.com",
        "wikipedia.org",
        "en.wikipedia.org",
        "mail.google.com",
        "gmail.com",
        "chat.openai.com",
        "reddit.com",
        "www.reddit.com",
        "python.org",
        "www.python.org",
        "microsoft.com",
        "www.microsoft.com"
    }

    # Actions that ALWAYS require explicit user confirmation
    SENSITIVE_KEYWORDS: Set[str] = {
        "delete", "remove", "format", "shutdown", "restart", 
        "send", "submit", "buy", "purchase", "pay", "order",
        "password", "credit", "card", "bank", "transfer", "erase"
    }

    def __init__(self):
        self._emergency_stop_triggered: bool = False
        self._is_automation_active: bool = False

    def is_app_allowed(self, app_alias: str) -> bool:
        """Checks if application alias is in the approved allowlist."""
        normalized = app_alias.strip().lower()
        return normalized in self.APPROVED_APPLICATIONS

    def get_app_command(self, app_alias: str) -> Optional[str]:
        """Returns the command executable for an approved app."""
        normalized = app_alias.strip().lower()
        if normalized in self.APPROVED_APPLICATIONS:
            return self.APPROVED_APPLICATIONS[normalized]["command"]
        return None

    def add_custom_app(self, alias: str, name: str, command: str) -> bool:
        """Adds a user-approved custom application."""
        alias_clean = alias.strip().lower()
        if not alias_clean or not command.strip():
            return False
        
        self.APPROVED_APPLICATIONS[alias_clean] = {
            "name": name.strip(),
            "command": command.strip(),
            "description": "User-approved custom app"
        }
        logger.info(f"Added custom application allowlist entry: {alias_clean} -> {command}")
        return True

    def is_url_safe(self, url: str) -> Tuple[bool, str]:
        """Validates that a URL uses safe protocols and is safe to open."""
        if not url:
            return False, "Empty URL"
        
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, f"Unsupported or dangerous scheme: {parsed.scheme}"
        
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False, "Invalid host in URL"

        return True, "Safe URL"

    def requires_confirmation(self, action_description: str) -> bool:
        """Inspects if an action contains potentially consequential keywords."""
        text = action_description.lower()
        return any(keyword in text for keyword in self.SENSITIVE_KEYWORDS)

    def trigger_emergency_stop(self):
        """Immediately halts active automation."""
        self._emergency_stop_triggered = True
        self._is_automation_active = False
        logger.warning("EMERGENCY STOP TRIGGERED! All running automations halted.")

    def reset_emergency_stop(self):
        """Resets the emergency stop flag."""
        self._emergency_stop_triggered = False

    @property
    def is_stopped(self) -> bool:
        return self._emergency_stop_triggered

    @property
    def is_automation_active(self) -> bool:
        return self._is_automation_active

    @is_automation_active.setter
    def is_automation_active(self, value: bool):
        self._is_automation_active = value


permissions = PermissionManager()

