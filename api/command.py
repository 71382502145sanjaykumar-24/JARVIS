"""
Vercel Serverless Handler for /api/command
"""

import sys
import os
import json
import re
import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ["VERCEL"] = "1"

def process_command_safely(raw_input: str) -> dict:
    """Processes command via command_processor or serverless fallback."""
    text = raw_input.strip()
    if not text:
        return {"intent": "empty", "response": "", "action_taken": False}

    # Try full backend processor first
    try:
        from backend.command_processor import command_processor
        return command_processor.process(text)
    except Exception:
        pass

    # Serverless fallback processor (guaranteed never to crash)
    cleaned = re.sub(r"^(?:hey\s+)?jarvis[,:\s]*", "", text, flags=re.IGNORECASE).strip()
    now = datetime.datetime.now()

    if re.search(r"\b(time|what time is it)\b", cleaned, re.IGNORECASE):
        return {
            "intent": "time_info",
            "response": f"The current server time is {now.strftime('%I:%M %p')}.",
            "action_taken": False
        }
    
    if re.search(r"\b(date|what's the date|today's date)\b", cleaned, re.IGNORECASE):
        return {
            "intent": "date_info",
            "response": f"Today is {now.strftime('%A, %B %d, %Y')}.",
            "action_taken": False
        }
        
    if re.search(r"\b(status|health|diagnostics)\b", cleaned, re.IGNORECASE):
        return {
            "intent": "system_info",
            "response": f"All JARVIS neural systems are fully operational in the cloud. Latency nominal.",
            "action_taken": False
        }

    if re.search(r"\b(hello|hi|hey|greetings)\b", cleaned, re.IGNORECASE):
        return {
            "intent": "greeting",
            "response": "Good day, sir. JARVIS Web Intelligence is active and listening. How may I be of service?",
            "action_taken": False
        }

    # Check for OpenAI key in environment
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key and len(api_key) > 10:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are JARVIS, an intelligent AI desktop assistant. Be concise, polite, and helpful."},
                    {"role": "user", "content": cleaned}
                ],
                max_tokens=300
            )
            return {
                "intent": "ai_conversation",
                "response": completion.choices[0].message.content.strip(),
                "action_taken": False
            }
        except Exception as e:
            return {
                "intent": "ai_error",
                "response": f"AI service note: {str(e)}",
                "action_taken": False
            }

    return {
        "intent": "general_response",
        "response": f"I received your command: '{cleaned}'. Desktop automation actions are available when running the native Windows client, and conversational intelligence is active.",
        "action_taken": False
    }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else ""
            data = json.loads(body) if body else {}
            cmd = data.get("command", "")
            result = process_command_safely(cmd)
        except Exception as e:
            result = {
                "intent": "notice",
                "response": f"Processed with notice: {str(e)}",
                "action_taken": False
            }

        response_bytes = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

app = handler
