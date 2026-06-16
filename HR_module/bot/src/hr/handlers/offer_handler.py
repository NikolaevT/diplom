from aiogram import F, Router
from aiogram.types import CallbackQuery
from loguru import logger

from src.hr.dto import OfferActionDto
from src.hr.service.bmk_it_client import bmk_it_client
from src.hr.service.telegram_client import telegram_client

router = Router(name="offer_handler")

CALLBACK_PREFIX = "offer:"


def _parse_offer_callback(data: str) -> tuple[str, str] | None:
    if not data.startswith(CALLBACK_PREFIX):
        return None
    parts = data.split(":", 2)
    if len(parts) != 3:
        return None
    return parts[1], parts[2]


async def _remove_keyboard(callback: CallbackQuery) -> None:
    if callback.message:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception as e:
            logger.debug(f"Не удалось убрать клавиатуру: {e}")


@router.callback_query(F.data.startswith(f"{CALLBACK_PREFIX}accept:"))
async def process_offer_accept(callback: CallbackQuery) -> None:
    parsed = _parse_offer_callback(callback.data or "")
    if not parsed or not callback.from_user:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    _, offer_id = parsed
    telegram_id = str(callback.from_user.id)
    action = OfferActionDto(offerId=offer_id, telegramId=telegram_id)

    try:
        await bmk_it_client.accept_offer(action)
    except Exception:
        logger.exception("Не удалось принять оффер")
        await callback.answer("Ошибка при отправке ответа. Попробуйте позже.", show_alert=True)
        return

    await _remove_keyboard(callback)
    await callback.answer()
    if callback.message:
        await callback.message.answer("Спасибо! Вы приняли оффер.")
        await telegram_client.send_documents_delivery_choice(telegram_id, offer_id)


@router.callback_query(F.data.startswith(f"{CALLBACK_PREFIX}reject:"))
async def process_offer_reject(callback: CallbackQuery) -> None:
    parsed = _parse_offer_callback(callback.data or "")
    if not parsed or not callback.from_user:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    _, offer_id = parsed
    telegram_id = str(callback.from_user.id)
    action = OfferActionDto(offerId=offer_id, telegramId=telegram_id)

    try:
        await bmk_it_client.reject_offer(action)
    except Exception:
        logger.exception("Не удалось отклонить оффер")
        await callback.answer("Ошибка при отправке ответа. Попробуйте позже.", show_alert=True)
        return

    await _remove_keyboard(callback)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Спасибо за ответ.\n" "Желаем вам успехов в дальнейшем поиске работы!"
        )
