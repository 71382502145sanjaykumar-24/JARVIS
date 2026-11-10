import pytest
from backend.ai_engine import ai_engine
from utils.config import config

def test_ai_engine_offline_fallback():
    # If no valid API key is set, the AI engine should return polite offline guidance
    old_key = config.openai_api_key
    config.openai_api_key = ""
    try:
        response = ai_engine.generate_response("Explain quantum computing")
        assert "local offline mode" in response or "not yet configured" in response
    finally:
        config.openai_api_key = old_key

def test_ai_engine_test_connection_no_key():
    old_key = config.openai_api_key
    config.openai_api_key = ""
    try:
        status = ai_engine.test_connection()
        assert status["success"] is False
        assert "missing" in status["message"].lower()
    finally:
        config.openai_api_key = old_key

