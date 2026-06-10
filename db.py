import os
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent / "instance" / "warnings.db"


def db_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB)))


def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS warning_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checked_at TEXT NOT NULL,
                city_name TEXT NOT NULL,
                warnings_text TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'manual'
            )
        """)

        columns = [
            row["name"]
            for row in conn.execute("PRAGMA table_info(warning_logs)").fetchall()
        ]

        if "source" not in columns:
            conn.execute("""
                ALTER TABLE warning_logs
                ADD COLUMN source TEXT NOT NULL DEFAULT 'manual'
            """)


def save_result(result: dict, source: str = "manual"):
    warnings_text = "、".join(result["warnings"]) or "発表なし"

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO warning_logs
                (checked_at, city_name, warnings_text, source)
            VALUES (?, ?, ?, ?)
            """,
            (
                result["checked_at"],
                result["city_name"],
                warnings_text,
                source,
            ),
        )


def latest_logs(limit: int = 50):
    with connect() as conn:
        return conn.execute(
            """
            SELECT id, checked_at, city_name, warnings_text, source
            FROM warning_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def cleanup_old_logs():
    with connect() as conn:
        conn.execute("""
            DELETE FROM warning_logs
            WHERE datetime(checked_at) < datetime('now', '-7 days')
        """)