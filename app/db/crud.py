import sqlite3

from app.config import DATABASE_PATH


def _get_conn():
    return sqlite3.connect(DATABASE_PATH)


def create_tables():
    conn = _get_conn()
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS weather_forecast (
            id INTEGER PRIMARY KEY,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            time TEXT NOT NULL,
            temperature_2m REAL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE (latitude, longitude, time)
        )"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS knowledge_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT NOT NULL,
            content TEXT NOT NULL,
            chunk_index INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT,
            sources TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )"""
    )

    conn.commit()
    conn.close()


# ──────────────── Weather ────────────────


def insert_weather(latitude: float, longitude: float, time: str, temperature_2m: float | None):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        """INSERT OR REPLACE INTO weather_forecast (latitude, longitude, time, temperature_2m)
           VALUES (?, ?, ?, ?)""",
        (latitude, longitude, time, temperature_2m),
    )
    conn.commit()
    conn.close()


def get_all_weather():
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM weather_forecast ORDER BY time DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_weather_by_location(latitude: float, longitude: float):
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM weather_forecast WHERE latitude = ? AND longitude = ? ORDER BY time",
        (latitude, longitude),
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_weather_by_date_range(start_date: str, end_date: str):
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM weather_forecast WHERE time >= ? AND time <= ? ORDER BY time",
        (start_date, end_date),
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ──────────────── Knowledge Base ────────────────


def insert_chunk(source_file: str, content: str, chunk_index: int = 0):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO knowledge_chunks (source_file, content, chunk_index) VALUES (?, ?, ?)",
        (source_file, content, chunk_index),
    )
    conn.commit()
    conn.close()


def search_chunks(query: str, limit: int = 5):
    """Recherche dans la base de connaissances.
    
    ATTENTION : utilise LIKE pour la recherche — c'est une recherche
    par sous-chaîne, pas une recherche sémantique.
    """
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM knowledge_chunks WHERE content LIKE ? LIMIT ?",
        (f"%{query}%", limit),
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_all_chunks():
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM knowledge_chunks ORDER BY source_file, chunk_index")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ──────────────── Conversations ────────────────


def save_conversation(question: str, answer: str, sources: str = ""):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO conversations (question, answer, sources) VALUES (?, ?, ?)",
        (question, answer, sources),
    )
    conn.commit()
    conn.close()


def get_conversations(limit: int = 20):
    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM conversations ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
