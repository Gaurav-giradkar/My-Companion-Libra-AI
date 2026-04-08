# 🤖 LIBRA – AI Companion System

**LIBRA** is a Flask-based AI companion designed for natural conversations, emotional awareness, and persistent memory. It intelligently switches between **Google Gemini (cloud AI)** and a **local offline fallback**, ensuring a smooth experience even without internet access.

---

## ✨ Features

### 🧠 Intelligent Conversation
- Uses **Google Gemini API** for high-quality responses
- Automatically falls back to **offline AI mode** if unavailable

### 💾 Persistent Memory
- Remembers:
  - Conversations
  - User preferences
  - Behavior patterns
- Retrieves relevant memories using **similarity scoring (embeddings)**

### 😊 Emotion Awareness
- Detects user emotion (happy, sad, angry, confused)
- Adjusts tone and responses dynamically

### 🔄 Flexible Storage System
- ☁ Firebase (cloud)
- 📁 Local JSON (fallback)
- Automatic switching between both

### 🎨 Modern UI Experience
- Futuristic chat interface
- Theme switching (blue, green, red, purple)
- Animated visual elements
- 📢 Optional text-to-speech (voice mode)

### ⚡ Resilient Design
- Lazy initialization of AI & database
- Works even without API keys
- Session-based user system

---

## 🏗️ Architecture Overview

```
Frontend (HTML/CSS/JS)
        ↓
Flask Backend (API Routes)
        ↓
AI Service (Gemini / Offline Mode)
        ↓
Memory System (Embeddings + Storage)
        ↓
Emotion + Behavior Engine
```

---

## 🛠 Tech Stack

| Category   | Technology |
|-----------|------------|
| Backend   | Python, Flask |
| AI        | Google Gemini API |
| Storage   | Firebase Admin SDK / Local JSON |
| Frontend  | HTML, CSS, JavaScript |
| Deployment| Gunicorn |
| Testing   | unittest |

---

## 📁 Project Structure

```
.
|-- app.py
|-- config/
|   `-- settings.py
|-- services/
|   |-- ai_service.py
|   `-- conversation_store.py
|-- static/
|   |-- css/style.css
|   `-- js/
|       |-- chat.js
|       |-- interface.js
|       `-- theme.js
|-- templates/
|   |-- base.html
|   |-- home.html
|   |-- about.html
|   `-- chat.html
|-- tests/
|-- utils/
|   |-- embedding.py
|   `-- emotion.py
`-- firebase_db.py
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
SECRET_KEY=change-this-in-production
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_KEY_PATH=config/firebase_key.json

LIBRA_STORE_BACKEND=auto
LOCAL_STORE_PATH=instance/libra_state.json

MAX_MESSAGE_LENGTH=500
LIBRA_MEMORY_LIMIT=5
LIBRA_MAX_STORED_MEMORIES=200

ENABLE_HTTPS_REDIRECT=false
```

### Storage Modes

| Mode       | Description |
|------------|------------|
| `auto`     | Use Firebase if available, else local |
| `firebase` | Prefer Firebase, fallback to local |
| `local`    | Always use local JSON |

---

## 🚀 Local Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

👉 Open in browser:  
http://127.0.0.1:5000

---

## 🧪 Running Tests

```bash
python -m unittest discover -s tests -v
```

Includes tests for:
- AI service behavior
- Memory retrieval system
- Embedding logic
- Emotion detection

---

## 🌐 API Endpoints

| Method | Endpoint        | Description |
|--------|----------------|------------|
| POST   | `/api/chat`    | Chat with LIBRA |
| GET    | `/api/joke`    | Random joke |
| GET    | `/api/dark-joke` | Dark humor joke |
| GET    | `/api/ping`    | Health check |

---

## 🚀 Deployment

Run with Gunicorn:

```bash
gunicorn app:app
```

If deploying behind a proxy:

```env
ENABLE_HTTPS_REDIRECT=true
```

---

## 📌 Key Highlights

- 🔹 Hybrid AI (Online + Offline fallback)
- 🔹 Custom embedding-based memory system (no heavy ML dependency)
- 🔹 Emotion-aware conversation engine
- 🔹 Behavior + preference learning
- 🔹 Modular and scalable backend design

---

## 🔮 Future Improvements

- Replace custom embeddings with advanced ML models
- Add authentication system (user accounts)
- Improve emotion detection using NLP models
- Deploy live with CI/CD pipeline

---

## 📜 License

This project is licensed under the **Apache License 2.0**.  
See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Gaurav Giradkar**

---

## ⭐ Support

If you like this project:
- ⭐ Star the repo
- 🍴 Fork it
- 🛠️ Contribute improvements

---