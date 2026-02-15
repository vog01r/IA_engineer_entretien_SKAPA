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

        c.execute(
            """CREATE TABLE IF NOT EXISTS weather_alerts (
                chat_id INTEGER PRIMARY KEY,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                label TEXT NOT NULL,
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


def _extract_keywords(query: str, min_len: int = 3) -> list[str]:
    """Extrait les mots significatifs (exclut stopwords courants)."""
    stopwords = {"quel", "quelle", "quels", "quelles", "le", "la", "les", "un", "une", "du", "des", "et", "ou", "en", "au", "aux", "à", "a", "est", "sont", "fait", "il", "elle"}
    words = "".join(c if c.isalnum() or c in " -" else " " for c in query.lower()).split()
    return [w for w in words if len(w) >= min_len and w not in stopwords]


def search_chunks(query: str, limit: int = 5):
    """Recherche dans la base de connaissances.

    Stratégie : extrait les mots-clés de la requête, cherche les chunks
    contenant AU MOINS un de ces mots (OR). Améliore le recall pour
    des questions en langage naturel ("quelle météo à Paris" → Paris, météo).

    Limitation : recherche lexicale, pas sémantique.
    Pour la production : migration vers pgvector/ChromaDB recommandée.
    """
    keywords = _extract_keywords(query)
    if not keywords:
        keywords = [query.strip()[:50]] if query.strip() else [""]

    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if len(keywords) == 1 and keywords[0]:
            c.execute(
                "SELECT * FROM knowledge_chunks WHERE content LIKE ? LIMIT ?",
                (f"%{keywords[0]}%", limit),
            )
        else:
            placeholders = " OR ".join(["content LIKE ?"] * len(keywords))
            params = [f"%{k}%" for k in keywords] + [limit]
            c.execute(
                f"SELECT * FROM knowledge_chunks WHERE {placeholders} LIMIT ?",
                params,
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


# ──────────────── Alertes proactives (bot Telegram) ────────────────


def upsert_alert(chat_id: int, latitude: float, longitude: float, label: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute(
            """INSERT INTO weather_alerts (chat_id, latitude, longitude, label)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(chat_id) DO UPDATE SET
                 latitude=excluded.latitude,
                 longitude=excluded.longitude,
                 label=excluded.label,
                 created_at=datetime('now')""",
            (chat_id, latitude, longitude, label),
        )
        conn.commit()


def delete_alert(chat_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM weather_alerts WHERE chat_id = ?", (chat_id,))
        conn.commit()


def get_alert(chat_id: int) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM weather_alerts WHERE chat_id = ?", (chat_id,))
        r = c.fetchone()
        return dict(r) if r else None


def get_all_alerts():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM weather_alerts")
        return [dict(r) for r in c.fetchall()]
