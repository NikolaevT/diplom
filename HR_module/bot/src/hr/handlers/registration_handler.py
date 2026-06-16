from datetime import datetime

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from src.hr.dto import CandidateDto
from src.hr.handlers.registration_states import RegistrationStates
from src.hr.service.bmk_it_client import bmk_it_client

router = Router(name="registration_handler")

ALREADY_REGISTERED_MESSAGE = "Вы уже зарегистрированы."
BIRTH_DATE_FORMAT_HINT = "Введите дату рождения в формате ДД.ММ.ГГГГ."


def parse_birth_date(value: str) -> str | None:
    """Проверяет дату рождения и возвращает нормализованную строку или None."""
    normalized = value.strip()
    try:
        parsed = datetime.strptime(normalized, "%d.%m.%Y")
    except ValueError:
        return None
    return parsed.strftime("%d.%m.%Y")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Старт регистрации кандидата.
    HR отправляет кандидату ссылку на бот, кандидат начинает анкету через /start.
    """
    if not message.from_user:
        return

    telegram_id = str(message.from_user.id)
    try:
        candidate = await bmk_it_client.get_candidate(telegram_id)
    except Exception:
        logger.exception("Не удалось проверить регистрацию кандидата")
        await message.answer("Не удалось связаться с БМК-ИТ. Попробуйте позже.")
        return

    if candidate is not None:
        await state.clear()
        await message.answer(ALREADY_REGISTERED_MESSAGE)
        return

    await state.set_state(RegistrationStates.waiting_full_name)
    await message.answer("Здравствуйте! Для регистрации отправьте, пожалуйста, ваше ФИО.")


@router.message(RegistrationStates.waiting_full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    full_name = (message.text or "").strip()
    if not full_name:
        await message.answer("ФИО не должно быть пустым. Отправьте, пожалуйста, ваше ФИО.")
        return

    await state.update_data(full_name=full_name)
    await state.set_state(RegistrationStates.waiting_birth_date)
    await message.answer(BIRTH_DATE_FORMAT_HINT)


@router.message(RegistrationStates.waiting_birth_date)
async def process_birth_date(message: Message, state: FSMContext) -> None:
    birth_date = parse_birth_date(message.text or "")
    if birth_date is None:
        await message.answer(
            f"Неверный формат даты. {BIRTH_DATE_FORMAT_HINT}"
        )
        return

    await state.update_data(birth_date=birth_date)
    await state.set_state(RegistrationStates.waiting_email)
    await message.answer("Введите вашу почту.")


@router.message(RegistrationStates.waiting_email)
async def process_email(message: Message, state: FSMContext) -> None:
    email = (message.text or "").strip()
    if not email:
        await message.answer("Почта не должна быть пустой. Введите вашу почту.")
        return
    if not message.from_user:
        return

    data = await state.get_data()
    candidate = CandidateDto(
        fullName=data["full_name"],
        birthDate=data["birth_date"],
        email=email,
        telegramId=str(message.from_user.id),
    )

    try:
        await bmk_it_client.register_candidate(candidate)
    except Exception:
        logger.exception("Не удалось зарегистрировать кандидата")
        await message.answer("Не удалось сохранить данные в БМК-ИТ. Попробуйте позже.")
        return

    await state.clear()
    await message.answer(
        "Спасибо! Вы зарегистрированы.\n"
        "HR сможет отправлять вам дальнейшие уведомления по процессу отбора."
    )
