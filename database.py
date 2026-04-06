import sqlite3
import os
import hashlib
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # MANA SHU QATOR BO'LISHI SHART
# 1. Baza yo'lini aniqlash (Faqat bitta baza fayli bo'lishi shart!)
DB_PATH = os.path.join(os.path.dirname(__file__), "pinokioai.db")

def _hash(password: str) -> str:
    """Parolni SHA-256 algoritmi orqali shifrlash"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_conn():
    """Ma'lumotlar bazasiga ulanish (Yagona funksiya)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# app.py rasmida qizil bo'lgan joy uchun nomni bir xil qildik
def get_db_connection():
    return get_conn()

def init_db():
    """Barcha jadvallarni yaratish"""
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT 'Yangi suhbat',
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            model_used TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()
    print("Baza muvaffaqiyatli yangilandi!")
def get_user_chats(user_id):
    """Foydalanuvchining barcha chatlarini olish"""
    conn = get_conn()
    chats = conn.execute('''
        SELECT id, title, created 
        FROM chats 
        WHERE user_id = ? 
        ORDER BY created DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(chat) for chat in chats]

def get_chat_history(chat_id, user_id):
    """Chat tarixini olish"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id=? AND user_id=? ORDER BY created ASC",
        (chat_id, user_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def register_user(username, email, password):
    conn = get_conn()
    try:
        hashed_pw = _hash(password)
        with conn: # 'with' ishlatilsa, commit() va xatolar avtomatik hal bo'ladi
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_pw)
            )
        return True, "Muvaffaqiyatli ro'yxatdan o'tdingiz!"
    except sqlite3.IntegrityError:
        return False, "Bu username yoki email allaqachon band!"
    except Exception as e:
        return False, f"Xatolik: {str(e)}"
    finally:
        conn.close() # Har qanday holatda ulanishni yopish shart

def login_user(email, password):
    """Foydalanuvchi loginini tekshirish"""
    conn = get_conn()
    hashed_pw = _hash(password)
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hashed_pw)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """ID orqali foydalanuvchini topish"""
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_chat(user_id, title="Yangi suhbat"):
    """Yangi chat ochish"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO chats (user_id, title) VALUES (?, ?)", (user_id, title))
    chat_id = cur.lastrowid
    conn.commit()
    conn.close()
    return chat_id

def save_message(chat_id, user_id, role, content, model_used=None):
    """Xabarni saqlash"""
    conn = get_conn()
    conn.execute(
        "INSERT INTO messages (chat_id, user_id, role, content, model_used) VALUES (?, ?, ?, ?, ?)",
        (chat_id, user_id, role, content, model_used)
    )
    conn.commit()
    conn.close()

def search_user_chats(user_id, query):
    """Chatlarni qidirish"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM chats WHERE user_id=? AND title LIKE ? ORDER BY created DESC",
        (user_id, f'%{query}%')
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]