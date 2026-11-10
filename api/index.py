"""
Vercel Serverless Function Entry Point for JARVIS (Flask WSGI)
"""

import sys
import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, Response, send_file

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure serverless environment variables
os.environ["VERCEL"] = "1"

from utils.helpers import get_system_metrics, get_current_time_str
from backend.command_processor import command_processor

app = Flask(__name__)

# Cache HTML content
HTML_FILE = ROOT_DIR / "public" / "index.html"
if HTML_FILE.exists():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        INDEX_HTML = f.read()
else:
    INDEX_HTML = "<h1>JARVIS AI is Online</h1>"

@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
@app.route("/index.html", methods=["GET"])
@app.route("/api", methods=["GET"])
def index():
    return Response(INDEX_HTML, mimetype="text/html")

@app.route("/assets/<path:filename>", methods=["GET"])
def serve_assets(filename):
    asset_file = ROOT_DIR / "public" / "assets" / filename
    if not asset_file.exists():
        asset_file = ROOT_DIR / "assets" / filename
    if asset_file.exists():
        return send_file(str(asset_file))
    return ("Asset Not Found", 404)

@app.route("/api/telemetry", methods=["GET"])
@app.route("/telemetry", methods=["GET"])
def telemetry():
    try:
        metrics = get_system_metrics()
        metrics["time"] = get_current_time_str()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({
            "cpu_percent": 15.0, 
            "ram_percent": 42.0, 
            "ram_used_gb": 6.8, 
            "ram_total_gb": 16.0, 
            "time": get_current_time_str()
        })

@app.route("/api/command", methods=["POST"])
@app.route("/command", methods=["POST"])
def run_command():
    try:
        data = request.get_json(silent=True) or {}
        cmd = data.get("command", "")
        result = command_processor.process(cmd)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "intent": "error", 
            "response": f"Server processing: {str(e)}", 
            "action_taken": False
        })

if __name__ == "__main__":
    app.run(port=8080)
