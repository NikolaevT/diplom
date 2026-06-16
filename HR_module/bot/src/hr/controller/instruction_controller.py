from fastapi import APIRouter

from src.hr.dto import InstructionDto
from src.hr.service.instruction_service import notify_instruction

router = APIRouter(
    prefix="/api/v1/instructions",
    tags=["instructions"],
)


@router.post("")
async def receive_instruction(instruction: InstructionDto):
    """Принимает инструкцию от БМК-ИТ и отправляет её кандидату в Telegram."""
    return await notify_instruction(instruction)
