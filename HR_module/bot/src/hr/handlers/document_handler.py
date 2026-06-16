from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.hr.config import settings

router = Router(name="document_handler")

DOCS_PREFIX = "docs:"


def _parse_docs_callback(data: str) -> tuple[str, str] | None:
    if not data.startswith(DOCS_PREFIX):
        return None
    parts = data.split(":", 2)
    if len(parts) != 3:
        return None
    return parts[1], parts[2]


@router.callback_query(F.data.startswith(f"{DOCS_PREFIX}mail:"))
async def process_documents_by_mail(callback: CallbackQuery) -> None:
    parsed = _parse_docs_callback(callback.data or "")
    if not parsed or not callback.message:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "<b>Отправьте документы на почту:</b>\n\n"
        f"📧 {settings.documents_email}\n\n"
        "Укажите в теме письма ваше ФИО."
    )


@router.callback_query(F.data.startswith(f"{DOCS_PREFIX}in_person:"))
async def process_documents_in_person(callback: CallbackQuery) -> None:
    parsed = _parse_docs_callback(callback.data or "")
    if not parsed or not callback.message:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "<b>Передайте документы лично бухгалтеру:</b>\n\n"
        f"📍 {settings.office_address}\n"
        f"🕐 {settings.office_hours}"
    )
