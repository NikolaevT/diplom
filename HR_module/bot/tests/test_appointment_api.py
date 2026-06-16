from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.hr.controller.appointment_controller import router
from src.hr.dto import AppointmentDto

app = FastAPI()
app.include_router(router)


@pytest.mark.asyncio
async def test_receive_appointment():
    appointment = AppointmentDto(
        appointmentId="apt-1",
        telegramId="12345",
        date="2026-05-26",
        time="14:00",
        location="Офис, ул. Примерная 1",
    )

    with patch(
        "src.hr.service.appointment_service.telegram_client.send_appointment",
        new_callable=AsyncMock,
        return_value=42,
    ) as send_mock:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/appointments",
                json=appointment.model_dump(by_alias=True),
            )

    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["messageId"] == 42
    send_mock.assert_awaited_once()
