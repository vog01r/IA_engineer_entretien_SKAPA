import sqlite3

from app.config import DATABASE_PATH


def create_tables():
    with sqlite3.connect(DATABASE_PATH) as conn:
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


# ──────────────── Weather ────────────────


def insert_weather(latitude: float, longitude: float, time: str, temperature_2m: float | None):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """INSERT OR REPLACE INTO weather_forecast (latitude, longitude, time, temperature_2m)
               VALUES (?, ?, ?, ?)""",
            (latitude, longitude, time, temperature_2m),
        )
        conn.commit()


def get_all_weather():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM weather_forecast ORDER BY time DESC")
        return [dict(r) for r in c.fetchall()]


def get_weather_by_location(latitude: float, longitude: float):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM weather_forecast WHERE latitude = ? AND longitude = ? ORDER BY time",
            (latitude, longitude),
        )
        return [dict(r) for r in c.fetchall()]


def get_weather_by_date_range(start_date: str, end_date: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM weather_forecast WHERE time >= ? AND time <= ? ORDER BY time",
            (start_date, end_date),
        )
        return [dict(r) for r in c.fetchall()]


# ──────────────── Knowledge Base ────────────────


def insert_chunk(source_file: str, content: str, chunk_index: int = 0):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO knowledge_chunks (source_file, content, chunk_index) VALUES (?, ?, ?)",
            (source_file, content, chunk_index),
        )
        conn.commit()


def search_chunks(query: str, limit: int = 5):
    """Recherche dans la base de connaissances.

    Utilise une recherche LIKE (lexicale, par sous-chaîne).
    Le terme de requête doit apparaître littéralement dans le contenu.

    Limitation : pas de recherche sémantique.
    Exemple : "quel temps fait-il ?" ne trouvera pas "prévisions météorologiques".
    Pour la production : migration vers PostgreSQL + pgvector ou ChromaDB recommandée.

    Gardé en l'état pour ce test (scope limité).
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM knowledge_chunks WHERE content LIKE ? LIMIT ?",
            (f"%{query}%", limit),
        )
        return [dict(r) for r in c.fetchall()]


def get_all_chunks():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM knowledge_chunks ORDER BY source_file, chunk_index")
        return [dict(r) for r in c.fetchall()]


# ──────────────── Conversations ────────────────


def save_conversation(question: str, answer: str, sources: str = ""):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO conversations (question, answer, sources) VALUES (?, ?, ?)",
            (question, answer, sources),
        )
        conn.commit()


def get_conversations(limit: int = 20):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM conversations ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in c.fetchall()]
