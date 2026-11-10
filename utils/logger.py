import os
import re
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "jarvis.log"

class SensitiveDataFilter(logging.Filter):
    """Filter that sanitizes API keys and sensitive tokens from log messages."""
    
    # Matches OpenAI keys (sk-...) or bearer tokens
    API_KEY_REGEX = re.compile(r"(sk-[a-zA-Z0-9_\-]{20,})|(Bearer\s+[a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE)

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.API_KEY_REGEX.sub("[REDACTED_API_KEY]", record.msg)
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(
                    self.API_KEY_REGEX.sub("[REDACTED_API_KEY]", a) if isinstance(a, str) else a
                    for a in record.args
                )
            elif isinstance(record.args, dict):
                record.args = {
                    k: (self.API_KEY_REGEX.sub("[REDACTED_API_KEY]", v) if isinstance(v, str) else v)
                    for k, v in record.args.items()
                }
        return True

def setup_logger(name: str = "JARVIS", level: int = logging.INFO) -> logging.Logger:
    """Creates and configures a structured logger with safety sanitization."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    sensitive_filter = SensitiveDataFilter()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(sensitive_filter)
    logger.addHandler(console_handler)

    # Rotating File Handler (Max 5MB per file, 3 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(sensitive_filter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()

