from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.getenv("SECRET_KEY", "libra-dev-secret")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
LIBRA_MODEL = os.getenv("LIBRA_MODEL", "models/gemini-2.5-flash")

FIREBASE_KEY_PATH = os.getenv(
    "FIREBASE_KEY_PATH",
    str(BASE_DIR / "config" / "firebase_key.json"),
)
STORE_BACKEND = os.getenv("LIBRA_STORE_BACKEND", "auto").strip().lower() or "auto"
LOCAL_STORE_PATH = os.getenv(
    "LOCAL_STORE_PATH",
    str(INSTANCE_DIR / "libra_state.json"),
)

MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "500"))
MEMORY_LIMIT = int(os.getenv("LIBRA_MEMORY_LIMIT", "5"))
MAX_STORED_MEMORIES = int(os.getenv("LIBRA_MAX_STORED_MEMORIES", "200"))

ENABLE_HTTPS_REDIRECT = _get_bool("ENABLE_HTTPS_REDIRECT", True)

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
PREFERRED_URL_SCHEME = "https"
