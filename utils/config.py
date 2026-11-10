import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from .env file if available
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    load_dotenv(override=True)


class JarvisConfig(BaseModel):
    """Central configuration for JARVIS Assistant."""
    
    # Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "database"
    assets_dir: Path = BASE_DIR / "assets"
    db_path: Path = BASE_DIR / "database" / "jarvis.db"

    # AI Configuration
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", "").strip())
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip())
    temperature: float = 0.7
    max_tokens: int = 1000

    # Voice Engine Configuration
    voice_engine: str = Field(default_factory=lambda: os.getenv("VOICE_ENGINE", "pyttsx3").strip())
    voice_rate: int = Field(default_factory=lambda: int(os.getenv("VOICE_RATE", "180")))
    voice_volume: float = Field(default_factory=lambda: float(os.getenv("VOICE_VOLUME", "1.0")))
    voice_index: int = 0
    speech_enabled: bool = Field(default_factory=lambda: os.getenv("SPEECH_ENABLED", "true").lower() == "true")

    # Speech Recognition Configuration
    energy_threshold: int = 300
    dynamic_energy_threshold: bool = True
    pause_threshold: float = 0.8
    phrase_time_limit: Optional[float] = 10.0

    # Desktop Automation & Safety
    automation_enabled: bool = Field(default_factory=lambda: os.getenv("AUTOMATION_ENABLED", "true").lower() == "true")
    require_confirmation: bool = Field(default_factory=lambda: os.getenv("REQUIRE_CONFIRMATION", "true").lower() == "true")
    safe_mode: bool = Field(default_factory=lambda: os.getenv("SAFE_MODE", "true").lower() == "true")

    # UI Preferences
    theme_mode: str = Field(default_factory=lambda: os.getenv("THEME_MODE", "dark"))
    accent_color: str = Field(default_factory=lambda: os.getenv("ACCENT_COLOR", "cyan"))
    start_minimized: bool = Field(default_factory=lambda: os.getenv("START_MINIMIZED", "false").lower() == "true")

    def has_valid_api_key(self) -> bool:
        """Check if an OpenAI API key is set and not empty or placeholder."""
        key = self.openai_api_key
        return bool(key and key != "your_openai_api_key_here" and len(key) > 10)

    def update_and_persist(self, **kwargs):
        """Update in-memory config and update .env file."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Persist updated values into .env
        env_lines = []
        existing_keys = set()
        
        if ENV_PATH.exists():
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and "=" in stripped:
                        k, _ = stripped.split("=", 1)
                        k = k.strip()
                        existing_keys.add(k)
                        match k:
                            case "OPENAI_API_KEY":
                                env_lines.append(f"OPENAI_API_KEY={self.openai_api_key}\n")
                            case "OPENAI_MODEL":
                                env_lines.append(f"OPENAI_MODEL={self.openai_model}\n")
                            case "VOICE_RATE":
                                env_lines.append(f"VOICE_RATE={self.voice_rate}\n")
                            case "VOICE_VOLUME":
                                env_lines.append(f"VOICE_VOLUME={self.voice_volume}\n")
                            case "VOICE_ENGINE":
                                env_lines.append(f"VOICE_ENGINE={self.voice_engine}\n")
                            case "SPEECH_ENABLED":
                                env_lines.append(f"SPEECH_ENABLED={'true' if self.speech_enabled else 'false'}\n")
                            case "AUTOMATION_ENABLED":
                                env_lines.append(f"AUTOMATION_ENABLED={'true' if self.automation_enabled else 'false'}\n")
                            case "REQUIRE_CONFIRMATION":
                                env_lines.append(f"REQUIRE_CONFIRMATION={'true' if self.require_confirmation else 'false'}\n")
                            case "SAFE_MODE":
                                env_lines.append(f"SAFE_MODE={'true' if self.safe_mode else 'false'}\n")
                            case "THEME_MODE":
                                env_lines.append(f"THEME_MODE={self.theme_mode}\n")
                            case "ACCENT_COLOR":
                                env_lines.append(f"ACCENT_COLOR={self.accent_color}\n")
                            case "START_MINIMIZED":
                                env_lines.append(f"START_MINIMIZED={'true' if self.start_minimized else 'false'}\n")
                            case _:
                                env_lines.append(line)
                    else:
                        env_lines.append(line)
        
        # Add keys that didn't exist
        defaults = {
            "OPENAI_API_KEY": self.openai_api_key,
            "OPENAI_MODEL": self.openai_model,
            "VOICE_RATE": str(self.voice_rate),
            "VOICE_VOLUME": str(self.voice_volume),
            "VOICE_ENGINE": self.voice_engine,
            "SPEECH_ENABLED": "true" if self.speech_enabled else "false",
            "AUTOMATION_ENABLED": "true" if self.automation_enabled else "false",
            "REQUIRE_CONFIRMATION": "true" if self.require_confirmation else "false",
            "SAFE_MODE": "true" if self.safe_mode else "false",
            "THEME_MODE": self.theme_mode,
            "ACCENT_COLOR": self.accent_color,
            "START_MINIMIZED": "true" if self.start_minimized else "false",
        }
        for k, v in defaults.items():
            if k not in existing_keys:
                env_lines.append(f"{k}={v}\n")

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(env_lines)


# Global configuration instance
config = JarvisConfig()

