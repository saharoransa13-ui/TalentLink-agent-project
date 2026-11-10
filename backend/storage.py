import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                request_id TEXT PRIMARY KEY,
                role_id TEXT NOT NULL,
                match_score REAL NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

def log_request(request_id: str, role_id: str, score: float):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO requests(request_id, role_id, match_score, created_at) VALUES (?, ?, ?, ?)",
            (request_id, role_id, score, datetime.now(timezone.utc).isoformat())
        )
