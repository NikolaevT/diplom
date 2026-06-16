import json
import sqlite3

from src.begemot.config.settings import settings


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.database_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _create_tables(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            birthday TEXT NOT NULL,
            username TEXT,
            phone_number TEXT NOT NULL DEFAULT ''
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS wishlists (
            user_id INTEGER PRIMARY KEY,
            items TEXT NOT NULL DEFAULT '[]',
            FOREIGN KEY (user_id) REFERENCES employees(user_id) ON DELETE CASCADE
        )
        """
    )


def _column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def _migrate_schema(cursor: sqlite3.Cursor) -> None:
    has_phone = _column_exists(cursor, "employees", "phone_number")

    if has_phone:
        cursor.execute(
            "SELECT user_id, name, birthday, username, phone_number "
            "FROM employees WHERE user_id IS NOT NULL"
        )
        employees = [
            (row[0], row[1], row[2], row[3], row[4] or "")
            for row in cursor.fetchall()
        ]
    else:
        cursor.execute(
            "SELECT user_id, name, birthday, username FROM employees WHERE user_id IS NOT NULL"
        )
        employees = [
            (row[0], row[1], row[2], row[3], "")
            for row in cursor.fetchall()
        ]

    wishlists_by_user: dict[int, str] = {}
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wishlists'")
    if cursor.fetchone():
        cursor.execute("SELECT user_id, items FROM wishlists")
        wishlists_by_user = {row[0]: row[1] or "[]" for row in cursor.fetchall()}

    cursor.execute("DROP TABLE IF EXISTS wishlists")
    cursor.execute("DROP TABLE IF EXISTS employees")
    _create_tables(cursor)

    for user_id, name, birthday, username, phone_number in employees:
        cursor.execute(
            "INSERT INTO employees (user_id, name, birthday, username, phone_number) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, name, birthday, username, phone_number),
        )
        items = wishlists_by_user.get(user_id, "[]")
        cursor.execute(
            "INSERT INTO wishlists (user_id, items) VALUES (?, ?)",
            (user_id, items),
        )


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    employees_exists = cursor.fetchone() is not None

    if employees_exists and not _column_exists(cursor, "employees", "phone_number"):
        _migrate_schema(cursor)
    else:
        _create_tables(cursor)

    conn.commit()
    conn.close()


def parse_wishlist_items(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return items if isinstance(items, list) else []
