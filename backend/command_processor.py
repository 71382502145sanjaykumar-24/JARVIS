"""
JARVIS Smart Command Processor
Intelligently classifies user intents and routes them to appropriate specialized engines.
"""

import re
from typing import Dict, Any, Optional
from utils.logger import logger
from utils.helpers import (
    get_current_time_str, 
    get_current_date_str, 
    format_system_status_summary
)
from utils.permissions import permissions
from backend.application_controller import app_controller
from backend.browser_controller import browser_controller
from backend.automation_engine import automation_engine
from backend.ai_engine import ai_engine
from backend.voice_engine import voice_engine
from database.db_manager import db

class CommandProcessor:
    """Classifies user requests and coordinates action execution."""

    # Regex patterns for fast local intent routing
    APP_OPEN_REGEX = re.compile(r"^(?:open|launch|start|run)\s+(?:the\s+)?([a-zA-Z0-9_\-\s]+)$", re.IGNORECASE)
    APP_CLOSE_REGEX = re.compile(r"^(?:close|quit|kill|terminate|exit)\s+(?:the\s+)?([a-zA-Z0-9_\-\s]+)$", re.IGNORECASE)
    
    SEARCH_REGEX = re.compile(r"^(?:search|look up|google|find)\s+(?:for\s+)?(.+?)(?:\s+on\s+(google|youtube))?$", re.IGNORECASE)
    
    TIME_REGEX = re.compile(r"\b(what time is it|current time|tell me the time|what's the time)\b", re.IGNORECASE)
    DATE_REGEX = re.compile(r"\b(what date is today|current date|what's the date|tell me today's date|today's date)\b", re.IGNORECASE)
    SYSTEM_INFO_REGEX = re.compile(r"\b(system status|system health|system diagnostics|battery status|cpu usage|ram usage)\b", re.IGNORECASE)
    
    TYPE_REGEX = re.compile(r"^(?:type|write|enter)\s+(?:the following text\s*:?\s*|text\s*:?\s*)?(.+)$", re.IGNORECASE)
    STOP_SPEECH_REGEX = re.compile(r"^(?:stop talking|be quiet|silence|mute|stop speech)$", re.IGNORECASE)
    EMERGENCY_STOP_REGEX = re.compile(r"^(?:emergency stop|abort|halt|stop all)$", re.IGNORECASE)

    def process(self, raw_input: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Main entry point to parse, route, execute, and record a command."""
        text = raw_input.strip()
        if not text:
            return {"intent": "empty", "response": "", "action_taken": False}

        # Normalize prefix: "hey jarvis", "jarvis"
        cleaned_text = re.sub(r"^(?:hey\s+)?jarvis[,:\s]*", "", text, flags=re.IGNORECASE).strip()
        if not cleaned_text:
            cleaned_text = text

        logger.info(f"Processing command: '{cleaned_text}' (raw: '{raw_input}')")

        # Save user message to database
        if conversation_id:
            db.add_message(conversation_id, "user", raw_input)

        result: Dict[str, Any] = {}

        # 1. Stop Speech
        if self.STOP_SPEECH_REGEX.match(cleaned_text):
            voice_engine.stop()
            result = {
                "intent": "stop_speech",
                "response": "Stopping voice output.",
                "action_taken": True
            }

        # 2. Emergency Stop
        elif self.EMERGENCY_STOP_REGEX.match(cleaned_text):
            automation_engine.emergency_stop()
            voice_engine.stop()
            result = {
                "intent": "emergency_stop",
                "response": "Emergency stop executed. All automations and voice speech halted.",
                "action_taken": True
            }

        # 3. Time Query
        elif self.TIME_REGEX.search(cleaned_text):
            time_str = get_current_time_str()
            result = {
                "intent": "time_info",
                "response": f"The current time is {time_str}.",
                "action_taken": False
            }

        # 4. Date Query
        elif self.DATE_REGEX.search(cleaned_text):
            date_str = get_current_date_str()
            result = {
                "intent": "date_info",
                "response": f"Today is {date_str}.",
                "action_taken": False
            }

        # 5. System Health / Metrics
        elif self.SYSTEM_INFO_REGEX.search(cleaned_text):
            status_summary = format_system_status_summary()
            result = {
                "intent": "system_info",
                "response": status_summary,
                "action_taken": False
            }

        # 6. Web Search
        elif self.SEARCH_REGEX.match(cleaned_text):
            match = self.SEARCH_REGEX.match(cleaned_text)
            query = match.group(1).strip()
            engine = match.group(2) or "google"
            
            # Avoid matching if query starts with "for" accidentally captured
            search_res = browser_controller.search_web(query, engine=engine)
            result = {
                "intent": "web_search",
                "response": search_res["message"],
                "action_taken": search_res["success"]
            }

        # 7. Close Application
        elif self.APP_CLOSE_REGEX.match(cleaned_text):
            app_target = self.APP_CLOSE_REGEX.match(cleaned_text).group(1).strip()
            close_res = app_controller.close_application(app_target)
            result = {
                "intent": "close_app",
                "response": close_res["message"],
                "action_taken": close_res["success"]
            }

        # 8. Open Application or Website
        elif self.APP_OPEN_REGEX.match(cleaned_text):
            target = self.APP_OPEN_REGEX.match(cleaned_text).group(1).strip()
            # Check if target is a known website
            if target.lower() in browser_controller.SITE_SHORTCUTS or "." in target:
                open_res = browser_controller.open_website(target)
                result = {
                    "intent": "open_browser",
                    "response": open_res["message"],
                    "action_taken": open_res["success"]
                }
            else:
                # Try application controller
                open_res = app_controller.open_application(target)
                result = {
                    "intent": "open_app",
                    "response": open_res["message"],
                    "action_taken": open_res["success"]
                }

        # 9. Type Text Automation
        elif self.TYPE_REGEX.match(cleaned_text) and len(cleaned_text.split()) > 2:
            text_to_type = self.TYPE_REGEX.match(cleaned_text).group(1).strip()
            type_res = automation_engine.type_text(text_to_type)
            result = {
                "intent": "desktop_automation",
                "response": type_res["message"],
                "action_taken": type_res["success"]
            }

        # 10. Conversational / General Intelligence Query via AI Engine
        else:
            response_text = ai_engine.generate_response(cleaned_text, conversation_id=conversation_id)
            result = {
                "intent": "ai_conversation",
                "response": response_text,
                "action_taken": False
            }

        # Save assistant message to database
        if conversation_id and result.get("response"):
            db.add_message(
                conversation_id, 
                "jarvis", 
                result["response"], 
                intent=result.get("intent")
            )

        return result


# Global command processor instance
command_processor = CommandProcessor()

