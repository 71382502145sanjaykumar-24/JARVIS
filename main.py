"""
JARVIS – Voice-Activated AI Virtual Assistant & Automation Tool
Unified Master Entry Point:
- Serves Flask WSGI Application for Cloud Web Deployments (Vercel / Render / Cloud)
- Launches CustomTkinter HUD for Local Desktop Execution (python main.py)
"""

import sys
import os
import re
import json
import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Create Flask WSGI Application
app = Flask(__name__, static_folder="public", static_url_path="")

@app.route("/")
@app.route("/index.html")
def serve_index():
    index_file = BASE_DIR / "public" / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/html; charset=utf-8")
    return Response("<h1>JARVIS AI is Online</h1>", mimetype="text/html; charset=utf-8")

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    assets_dir = BASE_DIR / "public" / "assets"
    if not (assets_dir / filename).exists():
        assets_dir = BASE_DIR / "assets"
    return send_from_directory(str(assets_dir), filename)

@app.route("/api/telemetry", methods=["GET", "OPTIONS"])
def api_telemetry():
    if request.method == "OPTIONS":
        return ("", 204)
    now = datetime.datetime.now()
    return jsonify({
        "cpu_percent": 14.5,
        "ram_percent": 41.2,
        "ram_used_gb": 6.6,
        "ram_total_gb": 16.0,
        "time": now.strftime("%I:%M %p"),
        "status": "online"
    })

@app.route("/api/command", methods=["POST", "OPTIONS"])
def api_command():
    if request.method == "OPTIONS":
        return ("", 204)
    data = request.get_json(silent=True) or {}
    raw_cmd = data.get("command", "").strip()
    if not raw_cmd:
        return jsonify({"intent": "empty", "response": "", "action_taken": False})

    # Try full backend processor if available
    try:
        from backend.command_processor import command_processor
        result = command_processor.process(raw_cmd)
        return jsonify(result)
    except Exception:
        pass

    # Built-in cloud NLP processor (guaranteed never to crash)
    cleaned = re.sub(r"^(?:hey\s+)?jarvis[,:\s]*", "", raw_cmd, flags=re.IGNORECASE).strip()
    now = datetime.datetime.now()

    if re.search(r"\b(time|what time is it)\b", cleaned, re.IGNORECASE):
        return jsonify({
            "intent": "time_info",
            "response": f"The current time is {now.strftime('%I:%M %p')}.",
            "action_taken": False
        })
    if re.search(r"\b(date|what's the date|today's date)\b", cleaned, re.IGNORECASE):
        return jsonify({
            "intent": "date_info",
            "response": f"Today is {now.strftime('%A, %B %d, %Y')}.",
            "action_taken": False
        })
    if re.search(r"\b(hello|hi|hey|greetings)\b", cleaned, re.IGNORECASE):
        return jsonify({
            "intent": "greeting",
            "response": "Good day, sir. JARVIS Web Intelligence is active and listening. How may I assist you?",
            "action_taken": False
        })
    if re.search(r"\b(status|health|diagnostics)\b", cleaned, re.IGNORECASE):
        return jsonify({
            "intent": "system_info",
            "response": "All JARVIS neural systems are fully operational in the cloud. Latency nominal.",
            "action_taken": False
        })

    # OpenAI completion if key is set in environment
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key and len(api_key) > 10:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are JARVIS, an advanced AI desktop assistant. Be concise, polite, and helpful."},
                    {"role": "user", "content": cleaned}
                ],
                max_tokens=300
            )
            return jsonify({
                "intent": "ai_conversation",
                "response": completion.choices[0].message.content.strip(),
                "action_taken": False
            })
        except Exception as e:
            return jsonify({
                "intent": "ai_error",
                "response": f"AI service note: {str(e)}",
                "action_taken": False
            })

    return jsonify({
        "intent": "general_response",
        "response": f"I have received your command: '{cleaned}'. Desktop application automation runs on the Windows client, and conversational intelligence is active.",
        "action_taken": False
    })

# Desktop Application Lifecycle
def handle_exit():
    """Performs clean shutdown of background workers and threads."""
    try:
        from backend.voice_engine import voice_engine
        from backend.speech_recognition import speech_recognizer
        voice_engine.stop()
        speech_recognizer.stop_listening()
    except Exception:
        pass

def main():
    """Main application lifecycle runner for Desktop HUD."""
    from utils.logger import logger
    from utils.config import config
    from utils.helpers import ensure_tcl_tk_environment

    ensure_tcl_tk_environment()

    logger.info("=" * 60)
    logger.info("Starting JARVIS AI Virtual Assistant & Automation Tool (Desktop)")
    logger.info(f"Root Directory: {BASE_DIR}")
    logger.info(f"OpenAI Key Configured: {config.has_valid_api_key()}")
    logger.info(f"Target OS: {sys.platform}")
    logger.info("=" * 60)

    try:
        from database.db_manager import db
        from frontend.dashboard import JarvisDashboard

        desktop_app = JarvisDashboard()

        def on_closing():
            handle_exit()
            desktop_app.destroy()
            sys.exit(0)

        desktop_app.protocol("WM_DELETE_WINDOW", on_closing)
        desktop_app.mainloop()

    except KeyboardInterrupt:
        handle_exit()
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error starting JARVIS desktop: {e}", exc_info=True)
        print(f"Fatal error starting JARVIS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
