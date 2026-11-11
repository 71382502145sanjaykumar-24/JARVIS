"""
Vercel Serverless Function Entry Point for JARVIS (/api)
"""

import json
import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        now = datetime.datetime.now()
        data = {
            "status": "online",
            "service": "JARVIS Web Intelligence",
            "time": now.strftime("%I:%M %p")
        }
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

app = handler
