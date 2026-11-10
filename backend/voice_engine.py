"""
JARVIS Voice Engine (Text-to-Speech)
Supports pyttsx3 (offline) and gTTS (online fallback), rate/pitch control, and non-blocking speech queues.
"""

import threading
import queue
import time
from typing import Optional, Callable, List, Dict, Any
try:
    import pyttsx3
except Exception:
    pyttsx3 = None
from utils.logger import logger
from utils.config import config

class VoiceEngine:
    """Non-blocking Text-to-Speech Engine."""

    def __init__(self):
        self.speech_queue: queue.Queue = queue.Queue()
        self.is_speaking: bool = False
        self._stop_requested: bool = False
        self._engine: Optional[pyttsx3.Engine] = None
        self._worker_thread: Optional[threading.Thread] = None
        
        # Callbacks for UI status update
        self.on_start_speaking: Optional[Callable[[], None]] = None
        self.on_stop_speaking: Optional[Callable[[], None]] = None

        self._init_engine()
        self._start_worker()

    def _init_engine(self):
        """Initializes the pyttsx3 engine with configured parameters."""
        if not pyttsx3:
            logger.info("pyttsx3 is not installed or available in this environment.")
            self._engine = None
            return

        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", config.voice_rate)
            self._engine.setProperty("volume", config.voice_volume)
            
            # Select default voice
            voices = self._engine.getProperty("voices")
            if voices and config.voice_index < len(voices):
                self._engine.setProperty("voice", voices[config.voice_index].id)
            logger.info("pyttsx3 Voice Engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 engine: {e}")
            self._engine = None

    def _start_worker(self):
        """Starts the dedicated background TTS worker thread."""
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def _process_queue(self):
        """Continuously pulls text from queue and speaks it."""
        while True:
            text = self.speech_queue.get()
            if text is None:
                break
            
            if not config.speech_enabled:
                self.speech_queue.task_done()
                continue

            try:
                self.is_speaking = True
                self._stop_requested = False
                if self.on_start_speaking:
                    try:
                        self.on_start_speaking()
                    except Exception as ex:
                        logger.error(f"Error in on_start_speaking callback: {ex}")

                # Ensure fresh engine instance to avoid COM thread apartment issues
                engine = pyttsx3.init()
                engine.setProperty("rate", config.voice_rate)
                engine.setProperty("volume", config.voice_volume)
                
                voices = engine.getProperty("voices")
                if voices and 0 <= config.voice_index < len(voices):
                    engine.setProperty("voice", voices[config.voice_index].id)

                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                logger.error(f"TTS playback error: {e}")
            finally:
                self.is_speaking = False
                if self.on_stop_speaking:
                    try:
                        self.on_stop_speaking()
                    except Exception as ex:
                        logger.error(f"Error in on_stop_speaking callback: {ex}")
                self.speech_queue.task_done()

    def speak(self, text: str):
        """Enqueues text to be spoken asynchronously."""
        if not text or not text.strip():
            return
        logger.info(f"Speaking: '{text[:60]}...'")
        self.speech_queue.put(text.strip())

    def stop(self):
        """Immediately stops speech output."""
        self._stop_requested = True
        try:
            # Clear remaining queue
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except queue.Empty:
                    break
            if self._engine:
                self._engine.stop()
        except Exception as e:
            logger.error(f"Error stopping voice engine: {e}")
        self.is_speaking = False
        if self.on_stop_speaking:
            self.on_stop_speaking()

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Returns list of installed system TTS voices."""
        voices_list = []
        try:
            if not self._engine:
                self._init_engine()
            if self._engine:
                for idx, v in enumerate(self._engine.getProperty("voices")):
                    voices_list.append({
                        "index": idx,
                        "id": v.id,
                        "name": v.name,
                        "languages": getattr(v, "languages", [])
                    })
        except Exception as e:
            logger.error(f"Failed to fetch voices: {e}")
        return voices_list

    def set_rate(self, rate: int):
        """Sets speech rate (speed)."""
        config.voice_rate = max(100, min(300, rate))
        config.update_and_persist(voice_rate=config.voice_rate)

    def set_volume(self, volume: float):
        """Sets speech volume (0.0 to 1.0)."""
        config.voice_volume = max(0.0, min(1.0, volume))
        config.update_and_persist(voice_volume=config.voice_volume)

    def set_voice(self, index: int):
        """Selects voice index."""
        config.voice_index = index
        config.update_and_persist(voice_index=index)


# Global Voice Engine instance
voice_engine = VoiceEngine()
