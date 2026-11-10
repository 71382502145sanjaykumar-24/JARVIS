"""
JARVIS Browser Controller
Handles authorized website navigation and web search queries.
"""

import webbrowser
import urllib.parse
from typing import Dict, Any
from utils.logger import logger
from utils.permissions import permissions
from database.db_manager import db

class BrowserController:
    """Manages browser opening and search queries securely."""

    SITE_SHORTCUTS = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "gmail": "https://mail.google.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit": "https://www.reddit.com",
        "wikipedia": "https://www.wikipedia.org",
        "chatgpt": "https://chat.openai.com",
    }

    def open_website(self, target: str) -> Dict[str, Any]:
        """Opens an approved website or URL in the default browser."""
        cleaned = target.strip().lower()

        # Check shortcuts first
        if cleaned in self.SITE_SHORTCUTS:
            url = self.SITE_SHORTCUTS[cleaned]
        elif cleaned.startswith("http://") or cleaned.startswith("https://"):
            url = target.strip()
        else:
            # Assume https://
            url = f"https://{cleaned}"

        is_safe, reason = permissions.is_url_safe(url)
        if not is_safe:
            msg = f"Cannot open URL: {reason}"
            logger.warning(msg)
            db.log_automation("open_browser", url, "denied", msg)
            return {"success": False, "message": msg}

        try:
            logger.info(f"Opening browser at: {url}")
            webbrowser.open(url)
            msg = f"Opening {cleaned.capitalize()}."
            db.log_automation("open_browser", url, "success", msg)
            return {"success": True, "message": msg}
        except Exception as e:
            error_msg = f"Failed to open browser: {str(e)}"
            logger.error(error_msg)
            db.log_automation("open_browser", url, "error", error_msg)
            return {"success": False, "message": error_msg}

    def search_web(self, query: str, engine: str = "google") -> Dict[str, Any]:
        """Performs a web search on Google or YouTube."""
        query_encoded = urllib.parse.quote_plus(query.strip())
        
        if engine.lower() == "youtube":
            url = f"https://www.youtube.com/results?search_query={query_encoded}"
            service_name = "YouTube"
        else:
            url = f"https://www.google.com/search?q={query_encoded}"
            service_name = "Google"

        try:
            logger.info(f"Searching {service_name} for '{query}'")
            webbrowser.open(url)
            msg = f"Searching {service_name} for '{query}'."
            db.log_automation("web_search", query, "success", msg)
            return {"success": True, "message": msg}
        except Exception as e:
            error_msg = f"Failed to perform search: {str(e)}"
            logger.error(error_msg)
            db.log_automation("web_search", query, "error", error_msg)
            return {"success": False, "message": error_msg}


# Global browser controller instance
browser_controller = BrowserController()

