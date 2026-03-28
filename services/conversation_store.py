from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from utils.embedding import cosine_similarity, get_embedding

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _memory_metadata(user_message: str) -> tuple[str, int]:
    normalized = user_message.lower()

    if "favorite" in normalized or "i like" in normalized:
        return "preference", 5
    if "who is" in normalized or "what is" in normalized:
        return "fact", 4
    if "i feel" in normalized or "i am" in normalized:
        return "emotion", 5
    if len(user_message) > 50:
        return "casual", 3
    return "casual", 1


class LocalConversationStore:
    backend_name = "local-json"

    def __init__(self, path: str, max_stored_memories: int = 200) -> None:
        self.path = Path(path)
        self.max_stored_memories = max_stored_memories

    def describe_backend(self) -> str:
        return self.backend_name

    def save_memory(self, username: str, user_msg: str, ai_msg: str) -> None:
        payload = self._load()
        user_bucket = self._user_bucket(payload, username)
        tag, importance = _memory_metadata(user_msg)

        user_bucket["memory"].append(
            {
                "user": user_msg,
                "ai": ai_msg,
                "embedding": get_embedding(user_msg),
                "tag": tag,
                "importance": importance,
                "timestamp": _utc_now(),
            }
        )
        user_bucket["memory"] = user_bucket["memory"][-self.max_stored_memories :]
        self._save(payload)

    def get_memory(self, username: str, query: str, limit: int = 5) -> list[tuple[str, str]]:
        payload = self._load()
        user_bucket = self._user_bucket(payload, username)
        memories = user_bucket["memory"]

        if not memories:
            return []

        query_vec = get_embedding(query)
        scored: list[tuple[float, dict[str, object]]] = []

        for item in memories:
            similarity = cosine_similarity(query_vec, item.get("embedding", []))
            recency_bonus = 0.02 if item is memories[-1] else 0.0
            importance_bonus = float(item.get("importance", 0)) / 100.0
            score = similarity + importance_bonus + recency_bonus
            scored.append((score, item))

        scored.sort(key=lambda item: item[0], reverse=True)
        top_memories = scored[:limit]

        if not any(score > 0 for score, _ in top_memories):
            recent_memories = sorted(
                memories,
                key=lambda item: item.get("timestamp", ""),
                reverse=True,
            )[:limit]
            return [(item["user"], item["ai"]) for item in reversed(recent_memories)]

        return [(item["user"], item["ai"]) for _, item in top_memories]

    def save_preference(self, username: str, key: str, value: str) -> None:
        payload = self._load()
        user_bucket = self._user_bucket(payload, username)
        user_bucket["preferences"][key] = value
        self._save(payload)

    def get_preferences(self, username: str) -> dict[str, str]:
        payload = self._load()
        user_bucket = self._user_bucket(payload, username)
        return dict(user_bucket["preferences"])

    def update_behavior(self, username: str, key: str, value: object) -> None:
        payload = self._load()
        user_bucket = self._user_bucket(payload, username)
        user_bucket["behavior"][key] = value
        self._save(payload)

    def get_behavior(self, username: str) -> dict[str, object]:
        payload = self._load()
        user_bucket = self._user_bucket(payload, username)
        return dict(user_bucket["behavior"])

    def _load(self) -> dict[str, object]:
        if not self.path.exists():
            return {"users": {}}

        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError:
            logger.warning("Local store was corrupted; resetting %s", self.path)
            return {"users": {}}

    def _save(self, payload: dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    @staticmethod
    def _user_bucket(payload: dict[str, object], username: str) -> dict[str, object]:
        users = payload.setdefault("users", {})
        return users.setdefault(
            username,
            {
                "memory": [],
                "preferences": {},
                "behavior": {},
            },
        )


class FirebaseConversationStore:
    backend_name = "firebase"

    def __init__(self, key_path: str) -> None:
        self.key_path = key_path
        self._db = None
        self._firestore = None
        self._firebase_admin = None

    def describe_backend(self) -> str:
        return self.backend_name

    def health_check(self) -> bool:
        try:
            self._get_db()
            return True
        except Exception as exc:
            logger.warning("Firebase store unavailable: %s", exc)
            return False

    def save_memory(self, username: str, user_msg: str, ai_msg: str) -> None:
        firestore = self._get_firestore()
        user_ref = self._user_ref(username)
        tag, importance = _memory_metadata(user_msg)

        user_ref.collection("memory").add(
            {
                "user": user_msg,
                "ai": ai_msg,
                "embedding": get_embedding(user_msg),
                "tag": tag,
                "importance": importance,
                "timestamp": firestore.SERVER_TIMESTAMP,
            }
        )

    def get_memory(self, username: str, query: str, limit: int = 5) -> list[tuple[str, str]]:
        firestore = self._get_firestore()
        docs = self._user_ref(username).collection("memory").stream()
        query_vec = get_embedding(query)
        scored: list[tuple[float, dict[str, object]]] = []

        for doc in docs:
            item = doc.to_dict()
            similarity = cosine_similarity(query_vec, item.get("embedding", []))
            importance_bonus = float(item.get("importance", 0)) / 100.0
            scored.append((similarity + importance_bonus, item))

        scored.sort(key=lambda item: item[0], reverse=True)
        top_memories = scored[:limit]

        if not top_memories:
            fallback_docs = (
                self._user_ref(username)
                .collection("memory")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )
            fallback = [doc.to_dict() for doc in fallback_docs]
            return [(item.get("user", ""), item.get("ai", "")) for item in fallback]

        return [(item["user"], item["ai"]) for _, item in top_memories]

    def save_preference(self, username: str, key: str, value: str) -> None:
        self._user_ref(username).collection("preferences").document(key).set({"value": value})

    def get_preferences(self, username: str) -> dict[str, str]:
        docs = self._user_ref(username).collection("preferences").stream()
        return {doc.id: doc.to_dict().get("value") for doc in docs}

    def update_behavior(self, username: str, key: str, value: object) -> None:
        self._user_ref(username).collection("behavior").document(key).set({"value": value})

    def get_behavior(self, username: str) -> dict[str, object]:
        docs = self._user_ref(username).collection("behavior").stream()
        return {doc.id: doc.to_dict().get("value") for doc in docs}

    def _user_ref(self, username: str):
        return self._get_db().collection("users").document(username)

    def _get_db(self):
        if self._db is not None:
            return self._db

        if not self.key_path:
            raise RuntimeError("FIREBASE_KEY_PATH is not configured.")
        if not os.path.exists(self.key_path):
            raise RuntimeError(f"Firebase key file not found at: {self.key_path}")

        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            credentials_obj = credentials.Certificate(self.key_path)
            firebase_admin.initialize_app(credentials_obj)

        self._firebase_admin = firebase_admin
        self._firestore = firestore
        self._db = firestore.client()
        return self._db

    def _get_firestore(self):
        if self._firestore is None:
            self._get_db()
        return self._firestore


def build_conversation_store(settings_module):
    local_store = LocalConversationStore(
        path=settings_module.LOCAL_STORE_PATH,
        max_stored_memories=settings_module.MAX_STORED_MEMORIES,
    )

    backend = getattr(settings_module, "STORE_BACKEND", "auto")
    if backend == "local":
        return local_store

    firebase_store = FirebaseConversationStore(settings_module.FIREBASE_KEY_PATH)
    if backend == "firebase":
        if firebase_store.health_check():
            return firebase_store
        logger.warning("Falling back to local store because Firebase is unavailable.")
        return local_store

    if firebase_store.health_check():
        return firebase_store

    logger.info("Using local JSON store because Firebase is unavailable.")
    return local_store
