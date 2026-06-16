import json

from src.begemot.config.database import get_connection, parse_wishlist_items

_EMPLOYEE_SELECT = """
    SELECT e.user_id, e.name, e.birthday, e.username, w.items
    FROM employees e
    LEFT JOIN wishlists w ON e.user_id = w.user_id
"""


def _row_to_employee(row: tuple) -> dict:
    return {
        "user_id": row[0],
        "name": row[1],
        "birthday": row[2],
        "username": row[3],
        "wishlist_items": parse_wishlist_items(row[4]),
    }


class EmployeeRepository:
    @staticmethod
    def load_all() -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(_EMPLOYEE_SELECT)
        employees = [_row_to_employee(row) for row in cursor.fetchall()]
        conn.close()
        return employees

    @staticmethod
    def load_birthdays() -> list[dict]:
        return EmployeeRepository.load_all()

    @staticmethod
    def exists(user_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM employees WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    @staticmethod
    def register(user_id: int, name: str, birthday: str, username: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (user_id, name, birthday, username, phone_number) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, name, birthday, username, ""),
        )
        cursor.execute(
            "INSERT INTO wishlists (user_id, items) VALUES (?, ?)",
            (user_id, "[]"),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def add(user_id: int, name: str, birthday: str, username: str) -> None:
        EmployeeRepository.register(user_id, name, birthday, username)

    @staticmethod
    def remove(name: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE name = ?", (name,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_wishlist_items(user_id: int) -> list[str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT items FROM wishlists WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return parse_wishlist_items(row[0] if row else None)

    @staticmethod
    def save_wishlist_items(user_id: int, items: list[str]) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO wishlists (user_id, items) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET items = excluded.items
            """,
            (user_id, json.dumps(items)),
        )
        conn.commit()
        conn.close()
