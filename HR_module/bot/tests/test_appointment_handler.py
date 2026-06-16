from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.hr.dto import AppointmentActionDto, AppointmentRescheduleDto
from src.hr.handlers.appointment_handler import (
    _parse_appointment_callback,
    process_appointment_agree,
    process_appointment_decline,
    process_reschedule_new_date,
)
from src.hr.service.bmk_it_client import BmkItClient


def test_parse_appointment_callback():
    assert _parse_appointment_callback("apt:agree:apt-1") == ("agree", "apt-1")
    assert _parse_appointment_callback("apt:reschedule:apt-2") == ("reschedule", "apt-2")
    assert _parse_appointment_callback("invalid") is None


def _make_callback(data: str, user_id: int = 12345) -> MagicMock:
    callback = MagicMock()
    callback.data = data
    callback.from_user = MagicMock()
    callback.from_user.id = user_id
    callback.message = AsyncMock()
    callback.message.edit_reply_markup = AsyncMock()
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()
    return callback


@pytest.mark.asyncio
async def test_agree_calls_bmk_it():
    callback = _make_callback("apt:agree:apt-1")

    with patch(
        "src.hr.handlers.appointment_handler.bmk_it_client.confirm_appointment",
        new_callable=AsyncMock,
    ) as confirm_mock:
        await process_appointment_agree(callback)

    confirm_mock.assert_awaited_once()
    action = confirm_mock.await_args.args[0]
    assert isinstance(action, AppointmentActionDto)
    assert action.appointment_id == "apt-1"
    assert action.telegram_id == "12345"
    callback.message.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_decline_calls_bmk_it():
    callback = _make_callback("apt:decline:apt-1")
    state = AsyncMock()
    state.clear = AsyncMock()

    with patch(
        "src.hr.handlers.appointment_handler.bmk_it_client.cancel_appointment",
        new_callable=AsyncMock,
    ) as cancel_mock:
        await process_appointment_decline(callback, state)

    cancel_mock.assert_awaited_once()
    state.clear.assert_awaited_once()


@pytest.mark.asyncio
async def test_reschedule_submits_to_bmk_it():
    message = MagicMock()
    message.text = "2026-05-27 15:00"
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.answer = AsyncMock()

    state = AsyncMock()
    state.get_data = AsyncMock(
        return_value={"appointment_id": "apt-1", "reason": "Занят на работе"}
    )
    state.clear = AsyncMock()

    with patch(
        "src.hr.handlers.appointment_handler.bmk_it_client.reschedule_appointment",
        new_callable=AsyncMock,
    ) as reschedule_mock:
        await process_reschedule_new_date(message, state)

    reschedule_mock.assert_awaited_once()
    payload = reschedule_mock.await_args.args[0]
    assert isinstance(payload, AppointmentRescheduleDto)
    assert payload.new_date == "2026-05-27 15:00"
    assert payload.reason == "Занят на работе"
    state.clear.assert_awaited_once()


@pytest.mark.asyncio
async def test_bmk_it_client_confirm():
    client = BmkItClient()
    action = AppointmentActionDto(appointmentId="apt-1", telegramId="12345")

    with patch.object(client, "_request", new_callable=AsyncMock) as request_mock:
        await client.confirm_appointment(action)

    request_mock.assert_awaited_once_with(
        "PUT",
        "/appointment/confirm",
        json={"appointmentId": "apt-1", "telegramId": "12345"},
    )
