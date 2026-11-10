# JARVIS Installation & Setup Guide

## System Prerequisites
- **Operating System:** Windows 10 or Windows 11 (64-bit)
- **Python:** Version 3.11, 3.12, or 3.13
- **Audio Hardware:** Working microphone and speakers/headphones
- **Internet Connection:** Required for OpenAI API queries and Google speech recognition

---

## Step-by-Step Installation (PowerShell)

### 1. Clone or Open Project
Open **Windows PowerShell** in the project directory:
```powershell
cd "c:\Users\Sanjay Kumar\.gemini\antigravity-ide\scratch\Jarvis"
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If script execution is disabled on your system, enable it for the current process by running: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*

### 3. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and add your OpenAI API key:
```ini
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```
*(Note: You can also configure or change the API key directly within the in-app **Settings** panel at any time.)*

---

## Running Automated Tests
Run the automated test suite to verify all subsystems:
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

---

## Launching JARVIS
Launch the desktop application:
```powershell
.\venv\Scripts\python.exe main.py
```

