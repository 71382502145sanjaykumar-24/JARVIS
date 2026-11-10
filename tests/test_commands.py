import pytest
from backend.command_processor import command_processor

def test_time_intent():
    res = command_processor.process("What time is it?")
    assert res["intent"] == "time_info"
    assert "current time" in res["response"].lower()

def test_date_intent():
    res = command_processor.process("Tell me today's date")
    assert res["intent"] == "date_info"
    assert "today is" in res["response"].lower()

def test_system_info_intent():
    res = command_processor.process("system status")
    assert res["intent"] == "system_info"
    assert "cpu load" in res["response"].lower()

def test_emergency_stop_intent():
    res = command_processor.process("Emergency stop")
    assert res["intent"] == "emergency_stop"
    assert "emergency stop executed" in res["response"].lower()

def test_stop_speech_intent():
    res = command_processor.process("stop talking")
    assert res["intent"] == "stop_speech"
    assert "stopping voice output" in res["response"].lower()

def test_empty_command():
    res = command_processor.process("   ")
    assert res["intent"] == "empty"
    assert res["response"] == ""

