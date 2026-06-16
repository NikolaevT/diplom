from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.hr.dto import AppointmentActionDto, AppointmentRescheduleDto
from src.hr.handlers.appointment_states import AppointmentRescheduleStates
from src.hr.service.bmk_it_client import bmk_it_client

router = Router(name="appointment_handler")

CALLBACK_PREFIX = "apt:"


def _parse_appointment_callback(data: str) -> tuple[str, str] | None:
    """
    Разбирает callback_data вида apt:agree:apt-1.
    Returns: (action, appointment_id) или None.
    """
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


@router.callback_query(F.data.startswith(f"{CALLBACK_PREFIX}agree:"))
async def process_appointment_agree(callback: CallbackQuery) -> None:
    parsed = _parse_appointment_callback(callback.data or "")
    if not parsed or not callback.from_user:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    _, appointment_id = parsed
    telegram_id = str(callback.from_user.id)
    action = AppointmentActionDto(appointmentId=appointment_id, telegramId=telegram_id)

    try:
        await bmk_it_client.confirm_appointment(action)
    except Exception:
        logger.exception("Не удалось подтвердить собеседование")
        await callback.answer("Ошибка при отправке ответа. Попробуйте позже.", show_alert=True)
        return

    await _remove_keyboard(callback)
    await callback.answer()
    if callback.message:
        await callback.message.answer("Спасибо! Вы подтвердили собеседование.")


@router.callback_query(F.data.startswith(f"{CALLBACK_PREFIX}decline:"))
async def process_appointment_decline(callback: CallbackQuery, state: FSMContext) -> None:
    parsed = _parse_appointment_callback(callback.data or "")
    if not parsed or not callback.from_user:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    _, appointment_id = parsed
    telegram_id = str(callback.from_user.id)
    action = AppointmentActionDto(appointmentId=appointment_id, telegramId=telegram_id)

    try:
        await bmk_it_client.cancel_appointment(action)
    except Exception:
        logger.exception("Не удалось отменить собеседование")
        await callback.answer("Ошибка при отправке ответа. Попробуйте позже.", show_alert=True)
        return

    await state.clear()
    await _remove_keyboard(callback)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Спасибо за ответ.\n" "Желаем вам успехов в дальнейшем поиске работы!"
        )


@router.callback_query(F.data.startswith(f"{CALLBACK_PREFIX}reschedule:"))
async def process_appointment_reschedule_start(callback: CallbackQuery, state: FSMContext) -> None:
    parsed = _parse_appointment_callback(callback.data or "")
    if not parsed or not callback.from_user:
        await callback.answer("Некорректные данные.", show_alert=True)
        return

    _, appointment_id = parsed
    await state.update_data(appointment_id=appointment_id)
    await state.set_state(AppointmentRescheduleStates.waiting_reason)

    await _remove_keyboard(callback)
    await callback.answer()
    if callback.message:
        await callback.message.answer("Укажите причину переноса собеседования.")


@router.message(AppointmentRescheduleStates.waiting_reason)
async def process_reschedule_reason(message: Message, state: FSMContext) -> None:
    reason = (message.text or "").strip()
    if not reason:
        await message.answer("Причина не должна быть пустой. Укажите причину переноса.")
        return

    await state.update_data(reason=reason)
    await state.set_state(AppointmentRescheduleStates.waiting_new_date)
    await message.answer("Укажите желаемую дату и время.")


@router.message(AppointmentRescheduleStates.waiting_new_date)
async def process_reschedule_new_date(message: Message, state: FSMContext) -> None:
    new_date = (message.text or "").strip()
    if not new_date:
        await message.answer("Дата и время не должны быть пустыми. Укажите желаемую дату и время.")
        return
    if not message.from_user:
        return

    data = await state.get_data()
    appointment_id = data.get("appointment_id")
    reason = data.get("reason")
    if not appointment_id or not reason:
        await state.clear()
        await message.answer("Сессия переноса истекла. Дождитесь нового приглашения.")
        return

    payload = AppointmentRescheduleDto(
        appointmentId=appointment_id,
        telegramId=str(message.from_user.id),
        reason=reason,
        newDate=new_date,
    )

    try:
        await bmk_it_client.reschedule_appointment(payload)
    except Exception:
        logger.exception("Не удалось отправить запрос на перенос")
        await message.answer("Не удалось отправить запрос. Попробуйте позже.")
        return

    await state.clear()
    await message.answer("Запрос на перенос отправлен HR. Ожидайте ответа.")
