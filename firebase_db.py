import firebase_admin
from firebase_admin import credentials, firestore
import os

# Load Firebase key from file OR environment variable
if not firebase_admin._apps:
    key_path = os.getenv("FIREBASE_KEY_PATH", "firebase_key.json")
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_user_ref(username):
    return db.collection("users").document(username)

def save_memory(username, user_msg, ai_msg):
    user_ref = get_user_ref(username)
    user_ref.collection("memory").add({
        "user": user_msg,
        "ai": ai_msg,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

def get_memory(username, limit=5):
    user_ref = get_user_ref(username)
    docs = (
        user_ref.collection("memory")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [(d.to_dict().get("user"), d.to_dict().get("ai")) for d in docs]

def save_preference(username, key, value):
    user_ref = get_user_ref(username)
    user_ref.collection("preferences").document(key).set({
        "value": value
    })

def get_preferences(username):
    user_ref = get_user_ref(username)
    docs = user_ref.collection("preferences").stream()
    return {d.id: d.to_dict().get("value") for d in docs}
