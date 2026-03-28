from __future__ import annotations

EMOTION_KEYWORDS = {
    "sad": {"sad", "tired", "low", "depressed", "lonely", "down", "upset", "hurt"},
    "happy": {"happy", "excited", "great", "awesome", "good", "joy", "glad"},
    "angry": {"angry", "annoyed", "frustrated", "irritated", "mad", "furious"},
    "confused": {"confused", "unclear", "lost", "stuck", "why", "what"},
}

HIGH_INTENSITY_MARKERS = {"very", "extremely", "really", "so", "totally", "deeply"}
LOW_INTENSITY_MARKERS = {"a bit", "slightly", "kind of", "sort of", "maybe"}


def detect_emotion(text: str) -> str:
    normalized = (text or "").lower()
    scores = {emotion: 0 for emotion in EMOTION_KEYWORDS}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                scores[emotion] += 1

    dominant_emotion, dominant_score = max(scores.items(), key=lambda item: item[1])
    return dominant_emotion if dominant_score > 0 else "neutral"


def detect_intensity(text: str) -> str:
    normalized = (text or "").lower()

    if any(marker in normalized for marker in LOW_INTENSITY_MARKERS):
        return "low"

    exclamation_count = normalized.count("!")
    if exclamation_count >= 2 or any(marker in normalized for marker in HIGH_INTENSITY_MARKERS):
        return "high"

    return "medium"
