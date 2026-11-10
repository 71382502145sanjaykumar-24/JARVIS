"""
JARVIS AI Engine
Integrates OpenAI API for intelligent conversation, context management, and reasoning.
"""

from typing import List, Dict, Any, Optional
import openai
from utils.logger import logger
from utils.config import config
from database.db_manager import db

JARVIS_SYSTEM_PROMPT = """You are JARVIS, an advanced, highly intelligent desktop AI assistant.
Your characteristics:
1. Tone: Refined, polite, confident, concise, and helpful (inspired by J.A.R.V.I.S.).
2. When answering voice commands: Keep explanations clear, well-structured, and directly to the point.
3. When providing code or technical explanations: Format neatly with clean markdown and concise guidance.
4. Always prioritize user safety and accuracy.
5. If the user asks about system state or desktop actions, acknowledge the action clearly.
"""

class AIEngine:
    """Manages LLM completions, conversation memory, and API status."""

    def __init__(self):
        self._client: Optional[openai.OpenAI] = None
        self._init_client()

    def _init_client(self):
        """Initializes OpenAI client if key is configured."""
        if config.has_valid_api_key():
            try:
                self._client = openai.OpenAI(api_key=config.openai_api_key)
                logger.info("OpenAI client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self._client = None
        else:
            self._client = None

    def refresh_client(self):
        """Re-initializes client after API key change in settings."""
        self._init_client()

    def test_connection(self) -> Dict[str, Any]:
        """Tests the OpenAI API connection and returns status."""
        if not config.has_valid_api_key():
            return {
                "success": False,
                "message": "OpenAI API key is missing. Please configure it in Settings or your .env file."
            }

        try:
            client = openai.OpenAI(api_key=config.openai_api_key)
            # Lightweight test completion
            response = client.chat.completions.create(
                model=config.openai_model,
                messages=[{"role": "user", "content": "Ping"}],
                max_tokens=5
            )
            return {
                "success": True,
                "message": f"Successfully connected to OpenAI ({config.openai_model})."
            }
        except openai.AuthenticationError:
            return {
                "success": False,
                "message": "Authentication failed: Invalid OpenAI API key."
            }
        except openai.RateLimitError:
            return {
                "success": False,
                "message": "Rate limit exceeded on OpenAI account."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }

    def generate_response(self, user_message: str, conversation_id: Optional[str] = None) -> str:
        """Generates an intelligent response using OpenAI API, maintaining conversation context."""
        if not config.has_valid_api_key():
            return (
                "I am running in local offline mode because an OpenAI API key is not yet configured. "
                "You can still open applications, websites, check system status, and control desktop automation. "
                "To enable full conversational AI intelligence, please enter your OpenAI API key in the Settings panel."
            )

        if not self._client:
            self._init_client()
            if not self._client:
                return "AI engine could not initialize. Please verify your OpenAI API key in Settings."

        # Build message history
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": JARVIS_SYSTEM_PROMPT}
        ]

        if conversation_id:
            recent_msgs = db.get_conversation_messages(conversation_id, limit=8)
            for msg in recent_msgs:
                role = "assistant" if msg["sender"] == "jarvis" else "user"
                messages.append({"role": role, "content": msg["content"]})

        # Append current user prompt
        messages.append({"role": "user", "content": user_message})

        try:
            response = self._client.chat.completions.create(
                model=config.openai_model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            reply = response.choices[0].message.content.strip()
            return reply

        except openai.AuthenticationError:
            logger.error("OpenAI Authentication error.")
            return "Authentication error: The provided OpenAI API key is invalid. Please check your settings."
        except openai.RateLimitError:
            logger.error("OpenAI Rate limit exceeded.")
            return "OpenAI rate limit reached. Please check your plan quota or try again in a few moments."
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI Connection error: {e}")
            return "Unable to connect to OpenAI servers. Please check your internet connection."
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return f"An unexpected error occurred while communicating with the AI service: {str(e)}"


# Global AI Engine instance
ai_engine = AIEngine()

