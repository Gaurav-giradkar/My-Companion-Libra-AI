def detect_emotion(text):
    text = text.lower()

    emotions = {
        "sad": ["sad", "tired", "low", "depressed", "lonely", "down"],
        "happy": ["happy", "excited", "great", "awesome", "good"],
        "angry": ["angry", "annoyed", "frustrated", "irritated"],
        "confused": ["confused", "don't understand", "what?", "why"],
    }

    for emotion, keywords in emotions.items():
        if any(word in text for word in keywords):
            return emotion

    return "neutral"

def detect_intensity(text):
    text = text.lower()

    if "very" in text or "extremely" in text or "so much" in text:
        return "high"

    if "a bit" in text or "slightly" in text:
        return "low"

    return "medium"