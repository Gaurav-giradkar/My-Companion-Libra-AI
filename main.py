from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import requests
import random

# -----------------------
# APP SETUP
# -----------------------
app = Flask(__name__)
load_dotenv()

# -----------------------
# API KEY CHECK
# -----------------------
api_key = os.getenv("GEMINI_API_KEY")
print("GEMINI KEY LOADED:", bool(api_key))

AI_ONLINE = False
client = None

try:
    if api_key:
        from google import genai
        client = genai.Client(api_key=api_key)
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
    data = request.get_json()
    user_message = data.get("message") if data else None

    if not user_message:
        return jsonify({"reply": "Say something, buddy 😄"}), 400

    try:
        # -----------------------
        # ONLINE MODE (GEMINI)
        # -----------------------
        if AI_ONLINE:
            prompt = (
                "You are LIBRA, a futuristic AI companion.\n\n"
                f"User: {user_message}\n"
                "LIBRA:"
            )

            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt
            )

            return jsonify({"reply": response.text})

        # -----------------------
        # OFFLINE MODE
        # -----------------------
        else:
            reply = offline_ai_reply(user_message)
            return jsonify({"reply": reply})

    except Exception as e:
        print("AI Error:", e)
        return jsonify({"reply": "LIBRA’s neural core just glitched ⚡"}), 500

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