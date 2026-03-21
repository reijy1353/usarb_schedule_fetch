"""
Centralized settings for the USARBy Project
Loads from .env (see .env.example for this one)

Use "pip install -e ." to download the USARBy package in editable mode
    or "pip install ." for non-editable mode
"""
import os
from pathlib import Path
from datetime import date, time, datetime

from dotenv import load_dotenv

# Load .env from project root (where this file lives)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


def _path(key: str, default: str) -> str:
    """Unpack a path (try to get path from .env)

    Args:
        key (str): .env variable
        default (str): Default statement

    Returns:
        str: Proper path
    """
    value = os.getenv(key, default).strip()
    if not value:
        return default
    p = Path(value)
    if not p.is_absolute():
        p = _PROJECT_ROOT / p
    return str(p.resolve())


def _str(key: str, default: str) -> str:
    """Unpack a string (try to get value from .env)

    Args:
        key (str): .env variable
        default (str): Default statement

    Returns:
        str: A value from .env or if non-existent the default
    """
    return os.getenv(key, default).strip() or default


def _academic_year_start() -> date:
    """Get the start of the academic year

    Returns:
        date: The start date (YYYY-MM-DD) of the acadmic year
    """

    today = date.today()
    year = today.year if today.month > 9 else today.year - 1
    return date(year, 9, 1)


# --- URLS ---
CALDAV_URL = _str("CALDAV_URL", "https://caldav.icloud.com")
MAIN_URL = _str("MAIN_URL", "https://orar.usarb.md")

# --- ICloud ---
ICLOUD_USERNAME = _str("ICLOUD_USERNAME", "user@icloud.com")
ICLOUD_PASSWORD = _str("ICLOUD_PASSWORD", "xxxx-yyyy-zzzz-qqqq")

# --- Calendar ---
CALENDAR_NAME = _str("CALENDAR_NAME", "USARBy Schedule")

# --- User settings ---
GROUP_NAME = _str("GROUP_NAME", "IT11Z")
SCHEDULE_PATH = _path("SCHEDULE_PATH", str(_PROJECT_ROOT / "schedule_snapshots" / "schedule_snapshot.json"))
OLD_SCHEDULE_PATH = _path("OLD_SCHEDULE_PATH", str(_PROJECT_ROOT / "schedule_snapshots" / "old_schedule_snapshot.json"))

# --- Other ---
FIRST_DAY = _academic_year_start()
FIRST_LESSON_TIME = time(8, 0)