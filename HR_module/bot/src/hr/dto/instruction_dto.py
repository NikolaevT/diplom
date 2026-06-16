from pydantic import BaseModel, ConfigDict, Field


class InstructionDto(BaseModel):
    """Данные инструкции от БМК-ИТ для отправки кандидату."""

    model_config = ConfigDict(populate_by_name=True)

    instruction_id: str = Field(..., alias="instructionId")
    telegram_id: str = Field(..., alias="telegramId")
    file_url: str = Field(..., alias="fileUrl")
    file_name: str = Field(default="Instruction.pdf", alias="fileName")
