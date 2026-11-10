"""
Vercel Serverless Function Entry Point for JARVIS
Exposes the web dashboard and API endpoints to Vercel's Python runtime.
"""

import sys
from pathlib import Path

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from web_server import JarvisWebHandler

# Vercel entrypoint handler
handler = JarvisWebHandler
app = handler
