from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.hr.controller.offer_controller import router
from src.hr.dto import OfferDto

app = FastAPI()
app.include_router(router)


@pytest.mark.asyncio
async def test_receive_offer():
    offer = OfferDto(
        offerId="offer-1",
        telegramId="12345",
        fileUrl="http://mock/offers/offer-1/file",
        fileName="Offer.pdf",
    )

    with (
        patch(
            "src.hr.service.offer_service._download_file",
            new_callable=AsyncMock,
            return_value=b"%PDF-1.4",
        ),
        patch(
            "src.hr.service.offer_service.telegram_client.send_offer",
            new_callable=AsyncMock,
            return_value=99,
        ) as send_mock,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/offers",
                json=offer.model_dump(by_alias=True),
            )

    assert resp.status_code == 200
    assert resp.json()["messageId"] == 99
    send_mock.assert_awaited_once()


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
async def test_offer_accept_calls_bmk_it():
    from src.hr.handlers.offer_handler import process_offer_accept

    callback = _make_callback("offer:accept:offer-1")

    with (
        patch(
            "src.hr.handlers.offer_handler.bmk_it_client.accept_offer",
            new_callable=AsyncMock,
        ) as accept_mock,
        patch(
            "src.hr.handlers.offer_handler.telegram_client.send_documents_delivery_choice",
            new_callable=AsyncMock,
        ) as docs_mock,
    ):
        await process_offer_accept(callback)

    accept_mock.assert_awaited_once()
    docs_mock.assert_awaited_once_with("12345", "offer-1")
