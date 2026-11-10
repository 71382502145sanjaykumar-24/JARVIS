import pytest
from backend.voice_engine import voice_engine
from utils.config import config

def test_voice_engine_parameters():
    voice_engine.set_rate(190)
    assert config.voice_rate == 190
    
    voice_engine.set_volume(0.9)
    assert config.voice_volume == 0.9

def test_voice_list():
    voices = voice_engine.get_available_voices()
    assert isinstance(voices, list)

def test_speech_queue():
    # Enqueue a message
    voice_engine.speak("Test speech phrase")
    assert not voice_engine.speech_queue.empty()
    # Clear queue
    voice_engine.stop()

