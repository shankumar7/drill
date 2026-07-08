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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cadet_id INTEGER,
            drill_type TEXT NOT NULL,
            score REAL NOT NULL,
            is_pass BOOLEAN NOT NULL,
            cycle_count INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cadet_id) REFERENCES cadets (id)
        )
    ''')
    try:
        cursor.execute("ALTER TABLE sessions ADD COLUMN cycle_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
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

def save_session(cadet_id: int, drill_type: str, score: float, is_pass: bool, cycle_count: int = 0) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (cadet_id, drill_type, score, is_pass, cycle_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (cadet_id, drill_type, score, is_pass, cycle_count))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_cadets() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            c.id, c.name, c.image_base64,
            COALESCE(AVG(s.score), 0) as avg_score,
            CASE WHEN COUNT(s.id) > 0 THEN (SUM(CASE WHEN s.is_pass THEN 1 ELSE 0 END) * 100.0 / COUNT(s.id)) ELSE 0 END as accuracy
        FROM cadets c
        LEFT JOIN sessions s ON c.id = s.cadet_id
        GROUP BY c.id
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_cadet_sessions(cadet_id: int) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, drill_type, score, is_pass, cycle_count, timestamp
        FROM sessions
        WHERE cadet_id = ?
        ORDER BY timestamp DESC
    ''', (cadet_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
