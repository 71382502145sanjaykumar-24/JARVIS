
"""
JARVIS Application Controller
Manages approved Windows application launching and process control.
"""

import subprocess
import shutil
import os
from typing import Dict, Any, Optional
from utils.logger import logger
from utils.permissions import permissions
from database.db_manager import db

class ApplicationController:
    """Controls application execution within authorized safety boundaries."""

    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Launches an approved application safely."""
        app_key = app_name.strip().lower()
        
        # Check permission allowlist
        if not permissions.is_app_allowed(app_key):
            # Attempt fuzzy lookup for common names
            matched_key = None
            for key, app_meta in permissions.APPROVED_APPLICATIONS.items():
                if app_key in key or key in app_key or app_key in app_meta["name"].lower():
                    matched_key = key
                    break
            
            if not matched_key:
                msg = f"Application '{app_name}' is not in the approved applications allowlist."
                logger.warning(msg)
                db.log_automation("open_app", app_name, "denied", msg)
                return {"success": False, "message": msg}
            app_key = matched_key

        command = permissions.get_app_command(app_key)
        app_meta = permissions.APPROVED_APPLICATIONS[app_key]

        try:
            # Launch via subprocess without blocking
            # If executable is on PATH or absolute path
            logger.info(f"Launching application: {app_meta['name']} ({command})")
            
            # Start process detached on Windows
            subprocess.Popen(
                command, 
                shell=True,
                creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0
            )

            success_msg = f"Opening {app_meta['name']}."
            db.log_automation("open_app", app_name, "success", success_msg)
            return {"success": True, "message": success_msg}
        except Exception as e:
            error_msg = f"Failed to launch application '{app_name}': {str(e)}"
            logger.error(error_msg)
            db.log_automation("open_app", app_name, "error", error_msg)
            return {"success": False, "message": error_msg}

    def close_application(self, app_name: str) -> Dict[str, Any]:
        """Closes an application safely using taskkill on Windows."""
        app_key = app_name.strip().lower()
        command = permissions.get_app_command(app_key)
        
        if not command:
            # Match against known apps
            for key, meta in permissions.APPROVED_APPLICATIONS.items():
                if app_key in key or key in app_key or app_key in meta["name"].lower():
                    command = meta["command"]
                    break

        if not command:
            return {"success": False, "message": f"Cannot close unknown application '{app_name}'."}

        # Normalize executable name for taskkill
        exe_name = command if command.endswith(".exe") else f"{command}.exe"
        try:
            subprocess.run(
                f"taskkill /f /im {exe_name}", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            msg = f"Closed {app_name}."
            db.log_automation("close_app", app_name, "success", msg)
            return {"success": True, "message": msg}
        except Exception as e:
            msg = f"Could not close '{app_name}': {e}"
            logger.error(msg)
            db.log_automation("close_app", app_name, "error", msg)
            return {"success": False, "message": msg}


# Global application controller instance
app_controller = ApplicationController()
