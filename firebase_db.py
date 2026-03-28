from __future__ import annotations

from config import settings
from services.conversation_store import build_conversation_store

_store = None


def _get_store():
    global _store
    if _store is None:
        _store = build_conversation_store(settings)
    return _store


def get_store_backend() -> str:
    return _get_store().describe_backend()


def save_memory(username: str, user_msg: str, ai_msg: str) -> None:
    _get_store().save_memory(username, user_msg, ai_msg)


def get_memory(username: str, query: str, limit: int = 5) -> list[tuple[str, str]]:
    return _get_store().get_memory(username, query, limit=limit)


def save_preference(username: str, key: str, value: str) -> None:
    _get_store().save_preference(username, key, value)


def get_preferences(username: str) -> dict[str, str]:
    return _get_store().get_preferences(username)


def update_behavior(username: str, key: str, value: object) -> None:
    _get_store().update_behavior(username, key, value)


def get_behavior(username: str) -> dict[str, object]:
    return _get_store().get_behavior(username)
