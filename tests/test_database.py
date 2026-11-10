import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from database.db_manager import DatabaseManager

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_jarvis.db"
    manager = DatabaseManager(db_path=db_file)
    yield manager
    # Ensure any background connections are released
    sqlite3.connect(str(db_file)).close()

def test_create_and_list_conversations(temp_db):
    conv_id = temp_db.create_conversation("Unit Test Session")
    assert conv_id is not None
    
    convs = temp_db.list_conversations()
    assert len(convs) == 1
    assert convs[0]["id"] == conv_id
    assert convs[0]["title"] == "Unit Test Session"

def test_add_and_retrieve_messages(temp_db):
    conv_id = temp_db.create_conversation("Message Test")
    
    msg_id1 = temp_db.add_message(conv_id, "user", "Hello Jarvis", intent="greeting")
    msg_id2 = temp_db.add_message(conv_id, "jarvis", "Hello sir", intent="greeting")
    
    assert msg_id1 > 0
    assert msg_id2 > 0
    
    msgs = temp_db.get_conversation_messages(conv_id)
    assert len(msgs) == 2
    assert msgs[0]["content"] == "Hello Jarvis"
    assert msgs[1]["content"] == "Hello sir"

def test_search_messages(temp_db):
    conv_id = temp_db.create_conversation("Search Test")
    temp_db.add_message(conv_id, "user", "What is artificial intelligence?")
    temp_db.add_message(conv_id, "jarvis", "AI is the simulation of human intelligence.")
    
    results = temp_db.search_messages("intelligence")
    assert len(results) == 2

def test_settings_storage(temp_db):
    temp_db.set_setting("theme", "cyber_dark")
    assert temp_db.get_setting("theme") == "cyber_dark"
    
    temp_db.set_setting("volume", 0.85)
    assert temp_db.get_setting("volume") == 0.85

def test_clear_all_conversations(temp_db):
    conv_id = temp_db.create_conversation("Wipe Test")
    temp_db.add_message(conv_id, "user", "Sample")
    
    success = temp_db.clear_all_conversations()
    assert success is True
    assert len(temp_db.list_conversations()) == 0
