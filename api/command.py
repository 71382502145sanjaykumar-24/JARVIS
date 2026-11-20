"""
Dedicated Serverless Handler for /api/command
"""

import os
import re
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["POST", "OPTIONS"])
@app.route("/api/command", methods=["POST", "OPTIONS"])
@app.route("/command", methods=["POST", "OPTIONS"])
def handle_command():
    if request.method == "OPTIONS":
        return ("", 204)
        
    data = request.get_json(silent=True) or {}
    raw_cmd = data.get("command", "").strip()
    user_api_key = data.get("apiKey", "").strip()

    if not raw_cmd:
        return jsonify({"intent": "empty", "response": "", "action_taken": False})

    cleaned = re.sub(r"^(?:hey\s+)?jarvis[,:\s]*", "", raw_cmd, flags=re.IGNORECASE).strip()
    now = datetime.datetime.now()

    # 1. Check for OpenAI API Key (from request or environment)
    api_key = user_api_key or os.environ.get("OPENAI_API_KEY", "")
    if api_key and len(api_key) > 10:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are J.A.R.V.I.S., a sophisticated, articulate, polite, and brilliant AI virtual assistant inspired by Tony Stark's system. Deliver concise, insightful, and helpful answers suitable for voice playback."
                    },
                    {"role": "user", "content": cleaned}
                ],
                max_tokens=600,
                temperature=0.7
            )
            reply = completion.choices[0].message.content.strip()
            return jsonify({
                "intent": "ai_conversation",
                "response": reply,
                "action_taken": False
            })
        except Exception as e:
            return jsonify({
                "intent": "ai_error",
                "response": f"OpenAI Notice: {str(e)}",
                "action_taken": False
            })

    # 2. Built-in fast NLP for standard questions if no API key is set
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
    if re.search(r"\b(hello|hi|hey|greetings|who are you)\b", cleaned, re.IGNORECASE):
        return jsonify({
            "intent": "greeting",
            "response": "Greetings, sir. I am J.A.R.V.I.S., your intelligent neural AI assistant. How may I assist you today?",
            "action_taken": False
        })
    if re.search(r"\b(status|health|diagnostics)\b", cleaned, re.IGNORECASE):
        return jsonify({
            "intent": "system_info",
            "response": "All JARVIS neural systems are fully operational in the cloud. Latency nominal.",
            "action_taken": False
        })

    return jsonify({
        "intent": "general_response",
        "response": f"I heard: '{cleaned}'. To enable full GPT conversational intelligence, connect your OpenAI API key using the '🔑 CONNECT AI KEY' button in the top bar.",
        "action_taken": False
    })

if __name__ == "__main__":
    app.run(port=8082)
