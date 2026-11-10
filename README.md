<div align="center">
  <img src="assets/jarvis_cyan.png" alt="JARVIS AI Virtual Assistant" width="320" style="border-radius: 16px; box-shadow: 0 0 25px #00f0ff;" />
  <br/>
  <h1>◈ J.A.R.V.I.S. ◈</h1>
  <p><b>Intelligent Voice-Activated AI Desktop Assistant & Automation Tool</b></p>
  <p><i>Next-generation desktop automation, neural speech synthesis, and cyberpunk HUD telemetry.</i></p>
</div>

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![UI-CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-00f0ff.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Tests-Pytest](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://docs.pytest.org/)
[![Platform-Windows](https://img.shields.io/badge/platform-Windows%2010%20%2F%2011-0078d7.svg)](https://www.microsoft.com/windows)

An intelligent, voice-activated desktop assistant engineered in Python with a futuristic dark cyberpunk HUD. Integrates OpenAI API conversational intelligence, real-time speech recognition, offline text-to-speech synthesis, system telemetry monitoring, and permission-regulated desktop automation.

---

## Key Features

- **Futuristic Iron Man / Cyberpunk HUD:** Built with CustomTkinter featuring glassmorphism panels, electric blue & arc-reactor cyan aesthetics, real-time system metrics, and quick action chips.
- **Dynamic Multi-Harmonic Waveform Visualizer:** Animated audio spectrum canvas showing live assistant states: `STANDBY`, `LISTENING`, `PROCESSING`, and `SPEAKING`.
- **Intelligent Speech Engine:** Speech recognition with background noise calibration via `SpeechRecognition` & `PyAudio`, combined with non-blocking offline speech synthesis via `pyttsx3`.
- **AI Brain & Context Memory:** OpenAI API integration (`gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`) with multi-turn context awareness and persistent SQLite storage.
- **Safe Desktop & Browser Automation:** Launch approved Windows applications (`Notepad`, `Calculator`, `Explorer`, `Cmd`, `VS Code`), open websites, conduct Google/YouTube searches, and execute keyboard automation with confirmation dialogs and an **Emergency Stop** switch.
- **Robust Local Offline Mode:** If no OpenAI API key is configured, JARVIS still operates all desktop automation, browser navigation, and system status queries locally.

---

## Architecture Overview

```
JARVIS/
├── main.py                     # Master application entry point
├── requirements.txt            # Project dependencies
├── .env.example                # Sample environment configuration
├── .gitignore                  # Git ignore rules
│
├── frontend/                   # UI / Presentation Layer
│   ├── dashboard.py            # Main futuristic HUD dashboard
│   ├── chat_interface.py       # Scrollable message stream
│   ├── voice_visualizer.py     # Animated waveform canvas
│   ├── settings.py             # Tabbed settings suite
│   └── components.py           # Futuristic UI widgets & design tokens
│
├── backend/                    # Core Logic & Engines
│   ├── ai_engine.py            # OpenAI LLM integration
│   ├── voice_engine.py         # Text-to-speech engine
│   ├── speech_recognition.py   # Microphone transcription
│   ├── command_processor.py    # Intent classifier & router
│   ├── automation_engine.py    # PyAutoGUI desktop automation
│   ├── browser_controller.py   # Web & browser controller
│   └── application_controller.py # Windows process launcher
│
├── database/                   # Data Layer
│   ├── db_manager.py           # SQLite manager
│   └── jarvis.db               # Local database
│
├── utils/                      # Utilities & Security
│   ├── config.py               # Pydantic configuration loader
│   ├── logger.py               # Sanitized rotating file logger
│   ├── permissions.py          # Allowlist and safety policies
│   └── helpers.py              # Telemetry & Tcl/Tk configurator
│
├── tests/                      # Automated Test Suite
│   ├── test_ai_engine.py
│   ├── test_voice_engine.py
│   ├── test_commands.py
│   └── test_database.py
│
└── docs/                       # Technical Documentation
    ├── architecture.md
    ├── installation.md
    └── user_guide.md
```

---

## Quick Start (Windows PowerShell)

```powershell
# 1. Activate Virtual Environment
.\venv\Scripts\Activate.ps1

# 2. Run Test Suite
.\venv\Scripts\python.exe -m pytest tests/ -v

# 3. Launch JARVIS Application
.\venv\Scripts\python.exe main.py
```

---

## Configuration

You can configure your settings via `.env` or using the in-app **⚙ SETTINGS** button:

```ini
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
VOICE_RATE=180
VOICE_VOLUME=1.0
VOICE_ENGINE=pyttsx3
SPEECH_ENABLED=true
AUTOMATION_ENABLED=true
REQUIRE_CONFIRMATION=true
SAFE_MODE=true
```

---

## Safety & Security

- **Credential Redaction:** API keys and bearer tokens are automatically sanitized and never printed to console or written to log files.
- **Application Allowlist:** Only approved executables in `utils/permissions.py` can be launched.
- **Fail-Safe & Emergency Stop:** Includes PyAutoGUI corner fail-safe and a persistent red **🛑 EMERGENCY STOP** button that immediately halts all active automations and voice speech.

