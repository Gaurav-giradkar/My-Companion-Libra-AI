from __future__ import annotations

import logging
import random

logger = logging.getLogger(__name__)

OFFLINE_RESPONSES = {
    "hello": [
        "Hello. I am here and ready to chat.",
        "Hi there. What would you like to talk about today?",
    ],
    "who are you": [
        "I am LIBRA, your companion for conversation, support, and quick help.",
    ],
    "help": [
        "I can chat, keep track of preferences, and still respond when cloud AI is offline.",
    ],
    "your name": [
        "My name is LIBRA.",
    ],
}

EMOTION_FALLBACKS = {
    "sad": [
        "I am here with you. Want to tell me what is weighing on you?",
        "That sounds heavy. We can take it one step at a time.",
    ],
    "happy": [
        "That is good to hear. What made today feel good?",
        "Nice. I am glad something is going well for you.",
    ],
    "angry": [
        "I hear the frustration. Want to unpack what caused it?",
        "Let us slow it down together and work through it clearly.",
    ],
    "confused": [
        "Let us break it down into smaller pieces.",
        "I can help simplify it. Tell me which part feels unclear.",
    ],
}

DEFAULT_OFFLINE_REPLIES = [
    "Interesting. Tell me a little more.",
    "I am following. What happened next?",
    "That makes sense. Want to keep going?",
    "I am listening.",
]


class LibraAIService:
    def __init__(self, api_key: str, model_name: str) -> None:
        self.api_key = api_key.strip()
        self.model_name = model_name
        self._model = None
        self._online_ready = False
        self._attempted_boot = False

    @property
    def is_online(self) -> bool:
        self._ensure_model()
        return self._online_ready

    def _ensure_model(self) -> None:
        if self._attempted_boot:
            return

        self._attempted_boot = True
        if not self.api_key:
            logger.info("Gemini API key not configured; running in offline mode.")
            return

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
            self._online_ready = True
            logger.info("Gemini model configured successfully.")
        except Exception as exc:
            logger.warning("Gemini initialization failed; using offline mode: %s", exc)
            self._model = None
            self._online_ready = False

    def generate_reply(
        self,
        user_message: str,
        emotion: str,
        intensity: str,
        preferences: dict[str, str],
        memory: list[tuple[str, str]],
        behavior: dict[str, object],
    ) -> tuple[str, str]:
        if self.is_online and self._model is not None:
            prompt = self._build_prompt(
                user_message=user_message,
                emotion=emotion,
                intensity=intensity,
                preferences=preferences,
                memory=memory,
                behavior=behavior,
            )

            try:
                response = self._model.generate_content(prompt)
                reply = (getattr(response, "text", "") or "").strip()
                if reply:
                    return reply, "online"
            except Exception as exc:
                logger.warning("Gemini reply failed; switching to offline reply: %s", exc)

        return offline_ai_reply(user_message, emotion, behavior), "offline"

    def _build_prompt(
        self,
        user_message: str,
        emotion: str,
        intensity: str,
        preferences: dict[str, str],
        memory: list[tuple[str, str]],
        behavior: dict[str, object],
    ) -> str:
        preference_lines = "\n".join(
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in preferences.items()
        ) or "- No saved preferences yet."

        memory_lines = "\n".join(
            f"- User: {user_text}\n  Libra: {reply_text}"
            for user_text, reply_text in memory
        ) or "- No relevant memory yet."

        behavior_lines = "\n".join(
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in behavior.items()
        ) or "- No behavior profile yet."

        return f"""
You are LIBRA, an intelligent AI companion.

Style:
- Calm, warm, and concise
- Helpful without sounding robotic
- Supportive when emotion is high, but still natural
- Use short replies when the user tends to prefer short messages

User emotion: {emotion}
Emotion intensity: {intensity}

Behavior profile:
{behavior_lines}

User preferences:
{preference_lines}

Relevant memory:
{memory_lines}

Current user message:
{user_message}

Reply as LIBRA:
""".strip()


def offline_ai_reply(
    user_message: str,
    emotion: str = "neutral",
    behavior: dict[str, object] | None = None,
) -> str:
    normalized = user_message.lower()
    behavior = behavior or {}

    for keyword, responses in OFFLINE_RESPONSES.items():
        if keyword in normalized:
            return random.choice(responses)

    if emotion in EMOTION_FALLBACKS:
        return random.choice(EMOTION_FALLBACKS[emotion])

    if behavior.get("short_style"):
        return "I am here."

    return random.choice(DEFAULT_OFFLINE_REPLIES)
