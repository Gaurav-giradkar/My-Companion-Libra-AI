# My Companion LIBRA AI

My Companion is a Flask web app for chatting with an AI companion that can:

- use Google Gemini when an API key is available
- fall back to an offline reply mode when cloud AI is unavailable
- remember recent conversations, preferences, and behavior signals
- use Firebase when configured, or a local JSON store when it is not

## Highlights

- Resilient startup with lazy Gemini and Firebase initialization
- Session-based users instead of one hardcoded profile
- Local similarity-based memory retrieval without extra ML dependencies
- Mobile-friendly chat UI with theme switching and optional text-to-speech
- Cleaner project structure with backend services and basic automated tests

## Tech Stack

- Python
- Flask
- Google Gemini
- Firebase Admin SDK
- HTML, CSS, JavaScript
- Gunicorn

## Project Structure

```text
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

## Environment Variables

Create a `.env` file for local development.

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

`LIBRA_STORE_BACKEND` supports:

- `auto`: use Firebase when available, otherwise local JSON storage
- `firebase`: prefer Firebase and fall back to local storage if unavailable
- `local`: always use local JSON storage

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Add the environment variables above.
4. Run the Flask app.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Running Tests

The included tests use the standard library `unittest` runner.

```bash
python -m unittest discover -s tests -v
```

## Deployment

Example Gunicorn command:

```bash
gunicorn app:app
```

If you deploy behind a proxy, keep `ENABLE_HTTPS_REDIRECT=true`.

## API Endpoints

- `POST /api/chat`
- `GET /api/joke`
- `GET /api/dark-joke`
- `GET /api/ping`

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
