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

from web_server import HTML_DASHBOARD
from utils.helpers import get_system_metrics, get_current_time_str
from backend.command_processor import command_processor

app = Flask(__name__)

@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def index():
    return Response(HTML_DASHBOARD, mimetype="text/html")

@app.route("/assets/<path:filename>", methods=["GET"])
def serve_assets(filename):
    asset_file = ROOT_DIR / "assets" / filename
    if asset_file.exists():
        return send_file(str(asset_file))
    return ("Asset Not Found", 404)

@app.route("/api/telemetry", methods=["GET"])
def telemetry():
    try:
        metrics = get_system_metrics()
        metrics["time"] = get_current_time_str()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({
            "cpu_percent": 0, 
            "ram_percent": 0, 
            "ram_used_gb": 0, 
            "ram_total_gb": 0, 
            "time": "--:--"
        })

@app.route("/api/command", methods=["POST"])
def run_command():
    try:
        data = request.get_json(silent=True) or {}
        cmd = data.get("command", "")
        result = command_processor.process(cmd)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "intent": "error", 
            "response": f"Server error: {str(e)}", 
            "action_taken": False
        })

if __name__ == "__main__":
    app.run(port=8080)
