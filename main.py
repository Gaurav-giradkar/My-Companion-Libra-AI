from flask import Flask, render_template, request, jsonify, redirect
from db import save_memory, get_memory, get_or_create_user, save_preference, get_preferences
import os
from dotenv import load_dotenv
import requests
import random

# -----------------------
# APP SETUP
# -----------------------
app = Flask(__name__)
load_dotenv()
LIBRA_USER_ID = get_or_create_user("gaurav")

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
    data = request.get_json()
    user_message = data.get("message") if data else None

    if not user_message:
        return jsonify({"reply": "Say something, buddy 😄"}), 400

    try:
        # -----------------------
        # LOAD MEMORY CONTEXT
        # -----------------------
        memory = get_memory(LIBRA_USER_ID, limit=5)
        prefs = get_preferences(LIBRA_USER_ID)
        pref_text = ""
        for k, v in prefs.items():
            pref_text += f"{k.replace('_',' ').title()}: {v}\n"


        context = ""
        for m in reversed(memory):
            context += f"User: {m[0]}\nLIBRA: {m[1]}\n"

        # -----------------------
        # ONLINE MODE (GEMINI)
        # -----------------------
        if AI_ONLINE:
            prompt = (
                "You are LIBRA, a futuristic AI companion with memory.\n"
                "You remember past conversations and user preferences. If there are conflicts, trust the MOST RECENT preference.\n\n"
                "Known user preferences:\n"
                + pref_text + "\n"
                + context +
                f"\nUser: {user_message}\n"
                "LIBRA:"
            )

            response = model.generate_content(prompt)
            libra_reply = response.text

            msg = user_message.lower()
            if "favorite color is" in msg:
                color = msg.split("favorite color is")[-1].strip()
                save_preference(LIBRA_USER_ID, "favorite_color", color)


            # -----------------------
            # SAVE TO MEMORY
            # -----------------------
            save_memory(LIBRA_USER_ID, user_message, libra_reply)

            return jsonify({"reply": libra_reply})

        # -----------------------
        # OFFLINE MODE
        # -----------------------
        else:
            reply = offline_ai_reply(user_message)

            # SAVE OFFLINE MEMORY TOO
            save_memory(LIBRA_USER_ID, user_message, reply)

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
    