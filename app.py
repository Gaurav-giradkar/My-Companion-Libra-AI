from __future__ import annotations

import logging
import re
import uuid

import requests
from flask import Flask, jsonify, redirect, render_template, request, session

from config import settings
from firebase_db import (
    get_behavior,
    get_memory,
    get_preferences,
    get_store_backend,
    save_memory,
    save_preference,
    update_behavior,
)
from services.ai_service import LibraAIService, offline_ai_reply
from utils.emotion import detect_emotion, detect_intensity

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

PREFERENCE_PATTERNS = (
    (
        re.compile(
            r"(?:my favorite color is|my favourite colour is|favorite color is|my color is)\s+([a-zA-Z][a-zA-Z\s-]{1,30})",
            re.IGNORECASE,
        ),
        "favorite_color",
    ),
    (
        re.compile(
            r"(?:call me|my name is)\s+([a-zA-Z][a-zA-Z\s'-]{1,40})",
            re.IGNORECASE,
        ),
        "preferred_name",
    ),
)


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(settings)
    app.secret_key = settings.SECRET_KEY
    ai_service = LibraAIService(settings.GEMINI_API_KEY, settings.LIBRA_MODEL)

    @app.before_request
    def prepare_request_context():
        session.permanent = True
        if "libra_user_id" not in session:
            session["libra_user_id"] = f"user-{uuid.uuid4().hex[:12]}"

        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        if (
            app.config["ENABLE_HTTPS_REDIRECT"]
            and forwarded_proto == "http"
            and not app.debug
        ):
            return redirect(request.url.replace("http://", "https://", 1), code=301)
        return None

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/chat")
    def chat():
        return render_template(
            "chat.html",
            max_message_length=app.config["MAX_MESSAGE_LENGTH"],
            store_backend=get_store_backend(),
        )

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        data = request.get_json(silent=True) or {}
        user_message = str(data.get("message", "")).strip()

        if not user_message:
            return jsonify({"reply": "Say something and I will jump in."}), 400

        if len(user_message) > app.config["MAX_MESSAGE_LENGTH"]:
            return (
                jsonify(
                    {
                        "reply": f"Keep it under {app.config['MAX_MESSAGE_LENGTH']} characters so I can respond well."
                    }
                ),
                400,
            )

        user_id = session["libra_user_id"]
        emotion = detect_emotion(user_message)
        intensity = detect_intensity(user_message)
        memory = safe_get_memory(user_id, user_message, app.config["MEMORY_LIMIT"])
        preferences = safe_get_preferences(user_id)
        behavior = safe_get_behavior(user_id)

        behavior_updates = derive_behavior_updates(user_message, emotion)
        for key, value in behavior_updates.items():
            safe_update_behavior(user_id, key, value)
        behavior.update(behavior_updates)

        preference_update = extract_preference_update(user_message)
        if preference_update:
            pref_key, pref_value = preference_update
            safe_save_preference(user_id, pref_key, pref_value)
            preferences[pref_key] = pref_value

        try:
            reply, mode = ai_service.generate_reply(
                user_message=user_message,
                emotion=emotion,
                intensity=intensity,
                preferences=preferences,
                memory=memory,
                behavior=behavior,
            )
        except Exception:
            logger.exception("AI generation failed for %s; using offline fallback.", user_id)
            reply = offline_ai_reply(user_message, emotion=emotion, behavior=behavior)
            mode = "offline"

        safe_save_memory(user_id, user_message, reply)

        return jsonify(
            {
                "reply": reply,
                "mode": mode,
                "store": get_store_backend(),
                "userId": user_id,
            }
        )

    @app.route("/api/dark-joke", methods=["GET"])
    def dark_joke():
        return jsonify({"joke": fetch_joke("Dark")})

    @app.route("/api/joke", methods=["GET"])
    def random_joke():
        return jsonify({"joke": fetch_joke("Programming,Misc,Pun")})

    @app.route("/favicon.ico")
    def favicon():
        return "", 204

    @app.route("/api/ping")
    def ping():
        return jsonify(
            {
                "status": "ok",
                "aiMode": "online" if ai_service.is_online else "offline",
                "store": get_store_backend(),
            }
        )

    return app


def fetch_joke(category: str) -> str:
    try:
        response = requests.get(
            f"https://v2.jokeapi.dev/joke/{category}?type=single",
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("type") == "single":
            return data.get("joke", "No joke available right now.")

        setup = data.get("setup", "").strip()
        delivery = data.get("delivery", "").strip()
        return f"{setup} - {delivery}".strip(" -")
    except Exception as exc:
        logger.warning("Joke fetch failed for %s: %s", category, exc)
        return "My joke circuits are offline right now."


def derive_behavior_updates(user_message: str, emotion: str) -> dict[str, object]:
    updates: dict[str, object] = {}

    if len(user_message) < 20:
        updates["short_style"] = True

    if "?" in user_message:
        updates["asks_questions"] = True

    if emotion == "sad":
        updates["emotional_state"] = "low"
    elif emotion == "happy":
        updates["emotional_state"] = "positive"
    elif emotion == "angry":
        updates["emotional_state"] = "tense"

    return updates


def extract_preference_update(user_message: str) -> tuple[str, str] | None:
    for pattern, key in PREFERENCE_PATTERNS:
        match = pattern.search(user_message)
        if match:
            value = match.group(1).strip(" .,!?:;")
            return key, value
    return None


def safe_get_memory(user_id: str, query: str, limit: int) -> list[tuple[str, str]]:
    try:
        return get_memory(user_id, query, limit=limit)
    except Exception as exc:
        logger.warning("Memory fetch failed for %s: %s", user_id, exc)
        return []


def safe_get_preferences(user_id: str) -> dict[str, str]:
    try:
        return get_preferences(user_id) or {}
    except Exception as exc:
        logger.warning("Preference fetch failed for %s: %s", user_id, exc)
        return {}


def safe_get_behavior(user_id: str) -> dict[str, object]:
    try:
        return get_behavior(user_id) or {}
    except Exception as exc:
        logger.warning("Behavior fetch failed for %s: %s", user_id, exc)
        return {}


def safe_update_behavior(user_id: str, key: str, value: object) -> None:
    try:
        update_behavior(user_id, key, value)
    except Exception as exc:
        logger.warning("Behavior update failed for %s: %s", user_id, exc)


def safe_save_preference(user_id: str, key: str, value: str) -> None:
    try:
        save_preference(user_id, key, value)
    except Exception as exc:
        logger.warning("Preference save failed for %s: %s", user_id, exc)


def safe_save_memory(user_id: str, user_message: str, reply: str) -> None:
    try:
        save_memory(user_id, user_message, reply)
    except Exception as exc:
        logger.warning("Memory save failed for %s: %s", user_id, exc)


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
