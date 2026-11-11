"""
Vercel Serverless Handler for /api/telemetry
"""

import sys
import os
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure serverless environment flag
os.environ["VERCEL"] = "1"

from utils.helpers import get_system_metrics, get_current_time_str

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            metrics = get_system_metrics()
            metrics["time"] = get_current_time_str()
        except Exception as e:
            metrics = {
                "cpu_percent": 18.0,
                "ram_percent": 45.0,
                "ram_used_gb": 7.2,
                "ram_total_gb": 16.0,
                "time": get_current_time_str()
            }
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(metrics).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

app = handler
