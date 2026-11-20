"""
Dedicated Serverless Handler for /api/telemetry
"""

import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", methods=["GET", "OPTIONS"])
@app.route("/api/telemetry", methods=["GET", "OPTIONS"])
@app.route("/telemetry", methods=["GET", "OPTIONS"])
def get_telemetry():
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

if __name__ == "__main__":
    app.run(port=8081)
