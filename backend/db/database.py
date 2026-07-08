import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cadets.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cadets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pin TEXT NOT NULL,
            image_base64 TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_cadet(name: str, pin: str, image_base64: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cadets (name, pin, image_base64)
        VALUES (?, ?, ?)
    ''', (name, pin, image_base64))
    cadet_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cadet_id

def login_cadet(pin: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, image_base64 FROM cadets
        WHERE pin = ?
    ''', (pin,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None
