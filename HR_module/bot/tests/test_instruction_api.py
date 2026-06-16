from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.hr.controller.instruction_controller import router
from src.hr.dto import InstructionDto

app = FastAPI()
app.include_router(router)


@pytest.mark.asyncio
async def test_receive_instruction():
    instruction = InstructionDto(
        instructionId="instr-1",
        telegramId="12345",
        fileUrl="http://mock/instructions/instr-1/file",
        fileName="Instruction.pdf",
    )

    with (
        patch(
            "src.hr.service.instruction_service._download_file",
            new_callable=AsyncMock,
            return_value=b"%PDF-1.4",
        ),
        patch(
            "src.hr.service.instruction_service.telegram_client.send_instruction",
            new_callable=AsyncMock,
            return_value=77,
        ) as send_mock,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/instructions",
                json=instruction.model_dump(by_alias=True),
            )

    assert resp.status_code == 200
    assert resp.json()["messageId"] == 77
    send_mock.assert_awaited_once()
