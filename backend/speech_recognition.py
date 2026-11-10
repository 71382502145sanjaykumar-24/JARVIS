"""
JARVIS Speech Recognition Engine
Captures microphone input, calibrates for ambient noise, and transcribes speech into text.
"""

import threading
import time
from typing import Optional, Callable
try:
    import speech_recognition as sr
except Exception:
    sr = None
from utils.logger import logger
from utils.config import config

class SpeechRecognitionEngine:
    """Manages audio capture and transcription via SpeechRecognition."""

    def __init__(self):
        if sr:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = config.energy_threshold
            self.recognizer.dynamic_energy_threshold = config.dynamic_energy_threshold
            self.recognizer.pause_threshold = config.pause_threshold
        else:
            self.recognizer = None
        
        self.is_listening: bool = False
        self._stop_listening_flag: bool = False
        self._listen_thread: Optional[threading.Thread] = None
        
        # UI Callbacks
        self.on_start_listening: Optional[Callable[[], None]] = None
        self.on_stop_listening: Optional[Callable[[], None]] = None
        self.on_recognized: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    def test_microphone_available(self) -> bool:
        """Verifies if at least one audio input device is accessible."""
        try:
            mics = sr.Microphone.list_microphone_names()
            return len(mics) > 0
        except Exception as e:
            logger.warning(f"Error checking microphone devices: {e}")
            return False

    def listen_once_async(self):
        """Starts a background thread to listen for a single spoken utterance."""
        if self.is_listening:
            logger.warning("Already listening.")
            return

        self._stop_listening_flag = False
        self._listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
        self._listen_thread.start()

    def _listen_worker(self):
        """Worker thread for microphone capture and speech-to-text."""
        self.is_listening = True
        if self.on_start_listening:
            try:
                self.on_start_listening()
            except Exception as e:
                logger.error(f"Error in on_start_listening callback: {e}")

        logger.info("Microphone active: Listening for user speech...")

        try:
            with sr.Microphone() as source:
                # Ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                
                if self._stop_listening_flag:
                    return

                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=7.0, 
                        phrase_time_limit=config.phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    logger.info("Speech recognition timed out (no speech detected).")
                    if self.on_error:
                        self.on_error("Listening timed out. No speech detected.")
                    return

            if self._stop_listening_flag:
                return

            logger.info("Processing captured audio...")
            try:
                # Transcribe speech using Google Speech Recognition service
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Speech Recognized: '{text}'")
                if self.on_recognized:
                    self.on_recognized(text)
            except sr.UnknownValueError:
                logger.warning("Speech recognition could not understand audio.")
                if self.on_error:
                    self.on_error("Could not understand audio. Please try again.")
            except sr.RequestError as e:
                logger.error(f"Could not request results from speech service: {e}")
                if self.on_error:
                    self.on_error("Speech recognition service connection error.")

        except Exception as e:
            logger.error(f"Microphone or PyAudio error: {e}")
            if self.on_error:
                self.on_error(f"Microphone error: {str(e)}")
        finally:
            self.is_listening = False
            if self.on_stop_listening:
                try:
                    self.on_stop_listening()
                except Exception as e:
                    logger.error(f"Error in on_stop_listening callback: {e}")

    def stop_listening(self):
        """Signals active listening thread to cancel."""
        self._stop_listening_flag = True
        self.is_listening = False
        if self.on_stop_listening:
            self.on_stop_listening()


# Global Speech Recognition instance
speech_recognizer = SpeechRecognitionEngine()

