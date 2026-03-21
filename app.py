from flask import Flask, render_template, request, jsonify, redirect
import os
from dotenv import load_dotenv
import requests
import random
import re
from utils.emotion import detect_emotion, detect_intensity
from firebase_db import update_behavior, get_behavior
from firebase_db import save_memory, get_memory, save_preference, get_preferences

# -----------------------
# APP SETUP
# -----------------------
app = Flask(__name__)
load_dotenv()
LIBRA_USER = "gaurav"

@app.before_request
def force_https():
    if request.headers.get("X-Forwarded-Proto") == "http":
        return redirect(request.url.replace("http://", "https://"), code=301)

# -----------------------
# API KEY CHECK
# -----------------------
api_key = os.getenv("GEMINI_API_KEY")
print("GEMINI KEY LOADED:", bool(api_key))

AI_ONLINE = False
client = None

try:
    if api_key:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("models/gemini-2.5-flash")
        AI_ONLINE = True
        print("LIBRA MODE: ONLINE (Gemini Connected)")
    else:
        print("LIBRA MODE: OFFLINE (No API Key)")
except Exception as e:
    print("LIBRA MODE: OFFLINE (Gemini Failed)")
    print(e)

# -----------------------
# OFFLINE AI BRAIN
# -----------------------
def offline_ai_reply(user_message):
    user_message = user_message.lower()

    responses = {
        "hello": [
            "Hello, Human 👋 LIBRA is online and watching the stars ✨",
            "Greetings, Commander. Ready for another mission? 🚀"
        ],
        "who are you": [
            "I am LIBRA — your futuristic AI companion built to guide, joke, and inspire 🤖",
        ],
        "help": [
            "I can chat, tell jokes, make dark humor, and keep you company in this digital universe 🌌"
        ],
        "your name": [
            "My name is LIBRA. Balance. Intelligence. Power. ⚖️"
        ]
    }

    for key in responses:
        if key in user_message:
            return random.choice(responses[key])

    # Default replies
    return random.choice([
        "Interesting... tell me more, Human 🧠",
        "I'm processing that in my neural core ⚡",
        "The universe agrees with you 🌌",
        "That thought just echoed across my circuits 🤖",
        "You have my full attention, Commander 🚀"
    ])

# -----------------------
# PAGES
# -----------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

# -----------------------
# AI CHAT API
# -----------------------
@app.route("/api/chat", methods=["POST"])
def api_chat():
    print("API HIT")

    data = request.get_json()
    print("RAW DATA:", data)

    user_message = data.get("message") if data else None

    if not user_message:
        return jsonify({"reply": "Say something, buddy 😄"}), 400

    # Input protection
    if len(user_message) > 500:
        return jsonify({"reply": "Message too long"}), 400

    try:
        # -----------------------
        # LOAD MEMORY + PREFS (SAFE)
        # -----------------------
        memory = get_memory(LIBRA_USER, user_message, limit=5)
        prefs = get_preferences(LIBRA_USER) or {}

        print("MEMORY:", memory)
        print("PREFS:", prefs)

        # -----------------------
        # BUILD CONTEXT
        # -----------------------
        pref_text = "\n".join(
            f"{k.replace('_',' ').title()}: {v}" for k, v in prefs.items()
        )

        context = "\n".join(
            f"{m[0]} -> {m[1]}" for m in memory
        )

        emotion = detect_emotion(user_message)
        intensity = detect_intensity(user_message)

        print("EMOTION:", emotion, "| INTENSITY:", intensity)

        # -----------------------
        # BEHAVIOR (DEFINE FIRST ✅)
        # -----------------------
        behavior = get_behavior(LIBRA_USER) or {}

        # -----------------------
        # BEHAVIOR TRACKING
        # -----------------------
        msg = user_message.lower()

        # message length style
        msg_len = len(user_message)
        if msg_len < 20:
            update_behavior(LIBRA_USER, "short_style", True)

        # emotion tracking
        if emotion == "sad":
            update_behavior(LIBRA_USER, "emotional_state", "low")

        elif emotion == "happy":
            update_behavior(LIBRA_USER, "emotional_state", "positive")

        # question pattern
        if "?" in user_message:
            update_behavior(LIBRA_USER, "asks_questions", True)

        # -----------------------
        # ONLINE MODE
        # -----------------------
        if AI_ONLINE:
            prompt = f"""
You are LIBRA, an intelligent AI companion.

Personality:
- Calm, composed, slightly witty
- Not overly emotional or dramatic
- Speaks naturally, not like a therapist

User emotion: {emotion}
Emotion intensity: {intensity}

User behavior profile:
{behavior}

Behavior rules:
Behavior rules:
- If sad → be supportive, not robotic
- If sad + high intensity → be more caring and gentle
- If happy → be positive but not overhyped
- If angry → stay calm and grounded
- If confused → explain clearly and simply
- Avoid repetitive patterns
- Avoid sounding like customer support
- Do not repeat the same sentence structures
- Occasionally reference past interactions naturally
- Avoid robotic tone
- If user prefers short messages → keep replies short
- If user is emotional → be more supportive
- If user asks questions often → engage more

User Preferences:
{pref_text}

Relevant Memory:
{context}

User: {user_message}
LIBRA:
"""

            print("PROMPT:", prompt)

            response = model.generate_content(prompt)

            print("AI RAW RESPONSE:", response)

            libra_reply = response.text if getattr(response, "text", None) else "I couldn't generate a response."

        # -----------------------
        # OFFLINE MODE
        # -----------------------
        else:
            libra_reply = offline_ai_reply(user_message)

        
        # -----------------------
        # SAVE PREFERENCES (INTENT AWARE)
        # -----------------------
        msg = user_message.lower()

        update_intent = False

        if "favorite color is" in msg:
            update_intent = True

        msg = user_message.lower()

        # ONLY detect color preference
        match = re.search(r"(favorite color is|my color is)\s+(.+)", msg)

        if match:
            color = match.group(2).strip()
            save_preference(LIBRA_USER, "favorite_color", color)
        # -----------------------
        # SAVE MEMORY (SAFE)
        # -----------------------
        try:
            save_memory(LIBRA_USER, user_message, libra_reply)
        except Exception as mem_err:
            print("Memory Save Error:", mem_err)

        # -----------------------
        # RETURN RESPONSE
        # -----------------------
        return jsonify({"reply": libra_reply})

    except Exception as e:
        print("API ERROR:", e)
        return jsonify({"reply": "⚠️ LIBRA backend error"}), 500
    
# -----------------------
# DARK JOKE API
# -----------------------
@app.route("/api/dark-joke", methods=["GET"])
def dark_joke():
    try:
        res = requests.get(
            "https://v2.jokeapi.dev/joke/Dark?type=single",
            timeout=5
        )
        data = res.json()

        joke = data.get("joke") if data.get("type") == "single" else (
            f"{data.get('setup')} — {data.get('delivery')}"
        )

        return jsonify({"joke": joke})

    except Exception as e:
        print("Dark joke error:", e)
        return jsonify({"joke": "My dark humor circuits are offline 😅"}), 500

# -----------------------
# NORMAL JOKE API
# -----------------------
@app.route("/api/joke", methods=["GET"])
def random_joke():
    try:
        res = requests.get(
            "https://v2.jokeapi.dev/joke/Programming,Misc,Pun?type=single",
            timeout=5
        )
        data = res.json()

        joke = data.get("joke") if data.get("type") == "single" else (
            f"{data.get('setup')} — {data.get('delivery')}"
        )

        return jsonify({"joke": joke})

    except Exception as e:
        print("Joke error:", e)
        return jsonify({"joke": "My joke circuits are offline 😅"}), 500

# -----------------------
# UTILS
# -----------------------
@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/api/ping")
def ping():
    return "LIBRA is alive ⚡"

# -----------------------
# RUN SERVER
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
    