import json
import sqlite3
from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from src.begemot.config import settings
from src.begemot.repository.employee_repository import EmployeeRepository
from src.begemot.service.reminder_service import ReminderService


@pytest.fixture
def memory_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """
        CREATE TABLE employees (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            birthday TEXT NOT NULL,
            username TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE wishlists (
            user_id INTEGER PRIMARY KEY,
            items TEXT NOT NULL DEFAULT '[]',
            FOREIGN KEY (user_id) REFERENCES employees(user_id) ON DELETE CASCADE
        )
        """
    )

    test_employees = [
        (1, "Иван Иванов", "15.05", "ivanov"),
        (2, "Петр Петров", "20.05", "petrov"),
        (3, "Мария Сидорова", "25.12", "sidorova"),
        (4, "Анна Козлова", "10.01", "kozlova"),
    ]
    for user_id, name, birthday, username in test_employees:
        cursor.execute(
            "INSERT INTO employees (user_id, name, birthday, username) VALUES (?, ?, ?, ?)",
            (user_id, name, birthday, username),
        )

    test_wishlists = [
        (1, json.dumps(["Книга", "Кофе"])),
        (2, json.dumps(["Наушники", "Чай"])),
        (3, json.dumps([])),
    ]
    for user_id, items in test_wishlists:
        cursor.execute(
            "INSERT INTO wishlists (user_id, items) VALUES (?, ?)",
            (user_id, items),
        )

    conn.commit()

    class _ConnectionWrapper:
        def __init__(self, connection: sqlite3.Connection) -> None:
            self._connection = connection

        def close(self) -> None:
            pass

        def __getattr__(self, name: str):
            return getattr(self._connection, name)

    def mock_connect():
        return _ConnectionWrapper(conn)

    monkeypatch.setattr("src.begemot.repository.employee_repository.get_connection", mock_connect)
    yield conn
    conn.close()


def test_load_all_employees(memory_db):
    employees = EmployeeRepository.load_all()
    assert len(employees) == 4
    assert employees[0]["name"] == "Иван Иванов"
    assert employees[0]["user_id"] == 1
    assert employees[0]["wishlist_items"] == ["Книга", "Кофе"]
    assert employees[1]["birthday"] == "20.05"


def test_load_birthdays(memory_db):
    birthdays = EmployeeRepository.load_birthdays()
    assert len(birthdays) == 4
    assert birthdays[0]["name"] == "Иван Иванов"
    assert birthdays[0]["user_id"] == 1
    assert birthdays[2]["wishlist_items"] == []


def test_save_wishlist_items(memory_db):
    EmployeeRepository.save_wishlist_items(3, ["Цветы", "Книга"])
    items = EmployeeRepository.get_wishlist_items(3)
    assert items == ["Цветы", "Книга"]


@pytest.fixture
def admin_ids(monkeypatch):
    monkeypatch.setattr(settings, "admin_ids", "999")


@pytest.mark.asyncio
async def test_birthday_reminder_no_upcoming(memory_db, admin_ids):
    mock_bot = AsyncMock()
    service = ReminderService(mock_bot)

    with (
        patch.object(EmployeeRepository, "load_all") as mock_employees,
        patch("src.begemot.service.reminder_service.datetime") as mock_datetime,
    ):
        mock_employees.return_value = [
            {
                "user_id": 1,
                "name": "Иван Иванов",
                "birthday": "15.12",
                "username": "ivanov",
                "wishlist_items": [],
            },
            {
                "user_id": 2,
                "name": "Петр Петров",
                "birthday": "20.12",
                "username": "petrov",
                "wishlist_items": [],
            },
        ]
        mock_datetime.now.return_value.date.return_value = date(2024, 6, 1)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        await service.send_birthday_reminder()

    mock_bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_birthday_reminder_with_upcoming(memory_db, admin_ids):
    mock_bot = AsyncMock()
    service = ReminderService(mock_bot)

    with (
        patch.object(EmployeeRepository, "load_all") as mock_employees,
        patch("src.begemot.service.reminder_service.datetime") as mock_datetime,
    ):
        today = date(2024, 5, 8)
        mock_datetime.now.return_value.date.return_value = today
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        mock_employees.return_value = [
            {
                "user_id": 1,
                "name": "Иван Иванов",
                "birthday": "15.05",
                "username": "ivanov",
                "wishlist_items": ["Книга", "Кофе"],
            },
            {
                "user_id": 2,
                "name": "Петр Петров",
                "birthday": "20.05",
                "username": "petrov",
                "wishlist_items": ["Наушники", "Чай"],
            },
            {
                "user_id": 3,
                "name": "Мария Сидорова",
                "birthday": "25.12",
                "username": "sidorova",
                "wishlist_items": [],
            },
        ]

        await service.send_birthday_reminder()

    assert mock_bot.send_message.call_count > 0
    calls_to_ivan = [call for call in mock_bot.send_message.call_args_list if call[0][0] == 1]
    assert len(calls_to_ivan) == 0
    calls_to_petr = [call for call in mock_bot.send_message.call_args_list if call[0][0] == 2]
    assert len(calls_to_petr) == 1
    calls_to_admin = [call for call in mock_bot.send_message.call_args_list if call[0][0] == 999]
    assert len(calls_to_admin) == 1


@pytest.mark.asyncio
async def test_birthday_reminder_empty_wishlist(memory_db, admin_ids):
    mock_bot = AsyncMock()
    service = ReminderService(mock_bot)

    with (
        patch.object(EmployeeRepository, "load_all") as mock_employees,
        patch("src.begemot.service.reminder_service.datetime") as mock_datetime,
    ):
        today = date(2024, 5, 8)
        mock_datetime.now.return_value.date.return_value = today
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        mock_employees.return_value = [
            {
                "user_id": 3,
                "name": "Мария Сидорова",
                "birthday": "15.05",
                "username": "sidorova",
                "wishlist_items": [],
            },
            {
                "user_id": 2,
                "name": "Петр Петров",
                "birthday": "20.05",
                "username": "petrov",
                "wishlist_items": [],
            },
        ]

        await service.send_birthday_reminder()

    message = mock_bot.send_message.call_args_list[0][0][1]
    assert "Мария Сидорова" in message
    assert "Вишлист пока пуст" in message
    assert "Книга" not in message


@pytest.mark.asyncio
async def test_monthly_birthdays(memory_db, admin_ids):
    mock_bot = AsyncMock()
    service = ReminderService(mock_bot)

    with (
        patch.object(EmployeeRepository, "load_all") as mock_employees,
        patch("src.begemot.service.reminder_service.datetime") as mock_datetime,
    ):
        today = date(2024, 12, 1)
        mock_datetime.now.return_value.date.return_value = today

        mock_employees.return_value = [
            {
                "user_id": 1,
                "name": "Иван Иванов",
                "birthday": "15.05",
                "username": "ivanov",
                "wishlist_items": [],
            },
            {
                "user_id": 3,
                "name": "Мария Сидорова",
                "birthday": "25.12",
                "username": "sidorova",
                "wishlist_items": [],
            },
            {
                "user_id": 4,
                "name": "Анна Козлова",
                "birthday": "10.01",
                "username": "kozlova",
                "wishlist_items": [],
            },
        ]

        await service.send_monthly_birthdays()

    assert mock_bot.send_message.call_count > 0
    message = mock_bot.send_message.call_args_list[0][0][1]
    assert "Анна Козлова" in message
    assert "10.01" in message
    assert "Иван Иванов" not in message


@pytest.mark.asyncio
async def test_monthly_birthdays_no_birthdays(memory_db, admin_ids):
    mock_bot = AsyncMock()
    service = ReminderService(mock_bot)

    with (
        patch.object(EmployeeRepository, "load_all") as mock_employees,
        patch("src.begemot.service.reminder_service.datetime") as mock_datetime,
    ):
        today = date(2024, 2, 1)
        mock_datetime.now.return_value.date.return_value = today

        mock_employees.return_value = [
            {
                "user_id": 1,
                "name": "Иван Иванов",
                "birthday": "15.05",
                "username": "ivanov",
                "wishlist_items": [],
            },
            {
                "user_id": 2,
                "name": "Петр Петров",
                "birthday": "20.05",
                "username": "petrov",
                "wishlist_items": [],
            },
        ]

        await service.send_monthly_birthdays()

    mock_bot.send_message.assert_not_called()
