import mysql.connector
import os

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("LIBRA_DB_PASSWORD", "@Gaurav13MySQL"),
        database="libra_ai"
    )

def get_or_create_user(username="default"):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
    else:
        cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        db.commit()
        user_id = cursor.lastrowid

    cursor.close()
    db.close()
    return user_id

def save_memory(user_id, user_msg, ai_msg):
    db = get_db()
    cursor = db.cursor()

    sql = """
    INSERT INTO memory (user_id, user_message, ai_reply)
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (user_id, user_msg, ai_msg))
    db.commit()

    cursor.close()
    db.close()

def get_memory(user_id, limit=5):
    db = get_db()
    cursor = db.cursor()

    sql = """
    SELECT user_message, ai_reply
    FROM memory
    WHERE user_id = %s
    ORDER BY id DESC
    LIMIT %s
    """
    cursor.execute(sql, (user_id, limit))
    rows = cursor.fetchall()

    cursor.close()
    db.close()
    return rows

def save_preference(user_id, key, value):
    db = get_db()
    cursor = db.cursor()
    sql = """
    INSERT INTO preferences (user_id, key_name, value)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE value = %s
    """
    cursor.execute(sql, (user_id, key, value, value))
    db.commit()
    cursor.close()
    db.close()

def get_preferences(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT key_name, value FROM preferences WHERE user_id = %s",
        (user_id,)
    )
    prefs = cursor.fetchall()
    cursor.close()
    db.close()
    return {k: v for k, v in prefs}
