import os
import firebase_admin
from firebase_admin import credentials, firestore
from utils.embedding import get_embedding
from utils.embedding import get_embedding
from config.settings import FIREBASE_KEY_PATH

# -------------------------
# FIREBASE INIT
# -------------------------
def init_firebase():
    if not firebase_admin._apps:

        # Validate env
        if not FIREBASE_KEY_PATH:
            raise RuntimeError("FIREBASE_KEY_PATH is not set in environment")

        # key_path = os.getenv("FIREBASE_KEY_PATH", "firebase_key.json")
        key_path = FIREBASE_KEY_PATH

        # Validate file exists
        if not os.path.exists(key_path):
            raise RuntimeError(f"Firebase key file not found at: {key_path}")

        # Initialize safely
        try:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            raise RuntimeError(f"Firebase initialization failed: {e}")

    return firestore.client()

db = init_firebase()

# -------------------------
# HELPERS
# -------------------------
def get_user_ref(username):
    return db.collection("users").document(username)

# -------------------------
# MEMORY SYSTEM
# -------------------------
def save_memory(username, user_msg, ai_msg):
    user_ref = get_user_ref(username)

    # -----------------------
    # TAGGING LOGIC
    # -----------------------
    msg = user_msg.lower()

    tag = "casual"
    importance = 1

    if "favorite" in msg or "i like" in msg:
        tag = "preference"
        importance = 5

    elif "who is" in msg or "what is" in msg:
        tag = "fact"
        importance = 4

    elif "i feel" in msg or "i am" in msg:
        tag = "emotion"
        importance = 5

    elif len(user_msg) > 50:
        importance = 3

    # -----------------------
    # SAVE STRUCTURED MEMORY
    # -----------------------
    embedding = get_embedding(user_msg)

    user_ref.collection("memory").add({
        "user": user_msg,
        "ai": ai_msg,
        "embedding": embedding,
        "tag": tag,
        "importance": importance,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

def get_memory(username, query, limit=5):
    user_ref = get_user_ref(username)

    docs = user_ref.collection("memory").stream()

    query_vec = get_embedding(query)

    scored = []

    for d in docs:
        data = d.to_dict()

        emb = data.get("embedding")
        if not emb:
            continue

        try:
            score = cosine_similarity(query_vec, emb)
            scored.append((score, data))
        except:
            continue

    # sort by relevance
    scored.sort(key=lambda x: x[0], reverse=True)

    top = scored[:limit]

    # fallback if no embeddings found
    if not top:
        docs = (
            user_ref.collection("memory")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [(d.to_dict().get("user"), d.to_dict().get("ai")) for d in docs]

    return [(d["user"], d["ai"]) for _, d in top]
# -------------------------
# PREFERENCES SYSTEM
# -------------------------
def save_preference(username, key, value):
    user_ref = get_user_ref(username)
    user_ref.collection("preferences").document(key).set({
        "value": value
    })

def get_preferences(username):
    user_ref = get_user_ref(username)
    docs = user_ref.collection("preferences").stream()
    return {d.id: d.to_dict().get("value") for d in docs}

def update_behavior(username, key, value):
    user_ref = get_user_ref(username)
    user_ref.collection("behavior").document(key).set({
        "value": value
    })

def get_behavior(username):
    user_ref = get_user_ref(username)
    docs = user_ref.collection("behavior").stream()
    return {d.id: d.to_dict().get("value") for d in docs}