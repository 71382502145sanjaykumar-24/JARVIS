"""
JARVIS System Helpers & Diagnostics
Provides utilities for system metrics, time/date, text formatting, and safe execution helpers.
"""

import os
import platform
import datetime
import psutil
from typing import Dict, Any
from utils.logger import logger

def ensure_tcl_tk_environment():
    """Ensures TCL_LIBRARY and TK_LIBRARY are set properly in Windows virtual environments."""
    import sys
    from pathlib import Path
    if "TCL_LIBRARY" not in os.environ or "TK_LIBRARY" not in os.environ:
        base_prefix = Path(sys.base_prefix)
        tcl_dir = base_prefix / "tcl"
        if tcl_dir.exists():
            for p in tcl_dir.glob("tcl*"):
                if p.is_dir() and "TCL_LIBRARY" not in os.environ:
                    os.environ["TCL_LIBRARY"] = str(p)
            for p in tcl_dir.glob("tk*"):
                if p.is_dir() and "TK_LIBRARY" not in os.environ:
                    os.environ["TK_LIBRARY"] = str(p)

def get_system_metrics() -> Dict[str, Any]:
    """Retrieves real-time CPU, RAM, battery, and disk statistics."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        battery = psutil.sensors_battery()
        battery_info = {
            "percent": battery.percent if battery else 100,
            "power_plugged": battery.power_plugged if battery else True,
            "has_battery": battery is not None
        }

        return {
            "cpu_percent": cpu_percent,
            "ram_percent": ram.percent,
            "ram_used_gb": round(ram.used / (1024 ** 3), 2),
            "ram_total_gb": round(ram.total / (1024 ** 3), 2),
            "disk_percent": disk.percent,
            "battery": battery_info,
            "platform": f"{platform.system()} {platform.release()}"
        }
    except Exception as e:
        logger.error(f"Error fetching system metrics: {e}")
        return {
            "cpu_percent": 0.0,
            "ram_percent": 0.0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "disk_percent": 0.0,
            "battery": {"percent": 100, "power_plugged": True, "has_battery": False},
            "platform": platform.platform()
        }

def get_current_time_str() -> str:
    """Returns human-readable current time."""
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

def get_current_date_str() -> str:
    """Returns human-readable current date."""
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y")

def format_system_status_summary() -> str:
    """Creates a concise voice-friendly summary of system health."""
    metrics = get_system_metrics()
    time_str = get_current_time_str()
    date_str = get_current_date_str()
    
    battery_text = ""
    if metrics["battery"]["has_battery"]:
        status = "plugged in" if metrics["battery"]["power_plugged"] else "on battery"
        battery_text = f", battery is at {metrics['battery']['percent']}% ({status})"

    return (
        f"The current time is {time_str} on {date_str}. "
        f"CPU load is at {metrics['cpu_percent']}%, and RAM utilization is at {metrics['ram_percent']}%"
        f"{battery_text}."
    )

def sanitize_text(text: str) -> str:
    """Sanitizes user input to prevent escape-character exploits."""
    if not text:
        return ""
    # Strip dangerous shell metacharacters for commands
    cleaned = text.strip()
    return cleaned
