"""
JARVIS SQLite Database Manager
Provides persistent storage for conversations, messages, settings, and automation event logs.
"""

import sqlite3
import datetime
import uuid
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.logger import logger
from utils.config import config

class DatabaseManager:
    """Manages SQLite database connections and transactions for JARVIS."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a connection configured for row dictionaries."""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes tables and indexes."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Conversations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        sender TEXT NOT NULL, -- 'user' or 'jarvis' or 'system'
                        content TEXT NOT NULL,
                        intent TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                    )
                """)

                # Settings table (Key-Value)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Automation Activity Logs
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS automation_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action_type TEXT NOT NULL,
                        target TEXT NOT NULL,
                        status TEXT NOT NULL, -- 'success', 'denied', 'error'
                        details TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_msg_conv ON messages(conversation_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_msg_time ON messages(timestamp)")
                
                conn.commit()
                logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    # =========================================================================
    # Conversation Methods
    # =========================================================================

    def create_conversation(self, title: str = "New Conversation") -> str:
        """Creates a new conversation session and returns its ID."""
        conv_id = str(uuid.uuid4())
        try:
            now_iso = datetime.datetime.now().isoformat()
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (conv_id, title, now_iso, now_iso)
                )
                conn.commit()
            return conv_id
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return conv_id

    def list_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists conversations sorted by last update."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to list conversations: {e}")
            return []

    def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetches messages belonging to a conversation."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, conversation_id, sender, content, intent, timestamp "
                    "FROM messages WHERE conversation_id = ? ORDER BY id ASC LIMIT ?",
                    (conversation_id, limit)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get messages for conversation {conversation_id}: {e}")
            return []

    def add_message(self, conversation_id: str, sender: str, content: str, intent: Optional[str] = None) -> int:
        """Adds a message to a conversation and updates conversation timestamp."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if conversation exists; create if not
                cursor.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
                if not cursor.fetchone():
                    # Generate title from first message
                    title = (content[:30] + "...") if len(content) > 30 else content
                    cursor.execute(
                        "INSERT INTO conversations (id, title) VALUES (?, ?)",
                        (conversation_id, title or "Session")
                    )

                now_iso = datetime.datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO messages (conversation_id, sender, content, intent, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (conversation_id, sender, content, intent, now_iso)
                )
                msg_id = cursor.lastrowid
                
                # Update conversation updated_at
                cursor.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (now_iso, conversation_id)
                )
                conn.commit()
                return msg_id or 0
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            return 0

    def delete_conversation(self, conversation_id: str) -> bool:
        """Deletes a conversation and all its messages."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
                cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
                conn.commit()
                logger.info(f"Deleted conversation {conversation_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False

    def clear_all_conversations(self) -> bool:
        """Wipes all conversations and messages."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages")
                cursor.execute("DELETE FROM conversations")
                conn.commit()
                logger.info("Cleared all conversation history")
                return True
        except Exception as e:
            logger.error(f"Failed to clear conversations: {e}")
            return False

    def search_messages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Searches across conversation history for keywords."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT m.id, m.conversation_id, m.sender, m.content, m.timestamp, c.title "
                    "FROM messages m JOIN conversations c ON m.conversation_id = c.id "
                    "WHERE m.content LIKE ? ORDER BY m.timestamp DESC LIMIT ?",
                    (f"%{query}%", limit)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []

    # =========================================================================
    # Settings & Preferences
    # =========================================================================

    def set_setting(self, key: str, value: Any) -> bool:
        """Saves a key-value setting."""
        try:
            val_str = json.dumps(value) if not isinstance(value, str) else value
            now_iso = datetime.datetime.now().isoformat()
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                    (key, val_str, now_iso)
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Retrieves a setting by key."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    val_str = row["value"]
                    try:
                        return json.loads(val_str)
                    except Exception:
                        return val_str
                return default
        except Exception as e:
            logger.error(f"Failed to get setting {key}: {e}")
            return default

    # =========================================================================
    # Automation Activity Log
    # =========================================================================

    def log_automation(self, action_type: str, target: str, status: str, details: Optional[str] = None):
        """Logs an automation execution event for safety tracking."""
        try:
            now_iso = datetime.datetime.now().isoformat()
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO automation_logs (action_type, target, status, details, timestamp) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (action_type, target, status, details or "", now_iso)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log automation activity: {e}")


# Global database manager instance
db = DatabaseManager()
