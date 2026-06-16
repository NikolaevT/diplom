from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from src.begemot.handlers.menu import show_main_menu
from src.begemot.repository.employee_repository import EmployeeRepository
from src.begemot.states.forms import RegistrationState

router = Router(name="registration")


@router.message(RegistrationState.name)
async def process_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(
        "Теперь введите вашу дату рождения в формате ДД.ММ (например, 15.05):"
    )
    await state.set_state(RegistrationState.birthday)


@router.message(RegistrationState.birthday)
async def process_birthday(message: types.Message, state: FSMContext) -> None:
    try:
        day, month = map(int, message.text.split("."))
        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError
    except ValueError:
        await message.answer(
            "Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ (например, 15.05):"
        )
        return

    await state.update_data(birthday=message.text)
    username = message.from_user.username
    if username:
        user_data = await state.get_data()
        EmployeeRepository.register(
            message.from_user.id,
            user_data["name"],
            user_data["birthday"],
            username,
        )
        await message.answer(
            "Регистрация завершена! Теперь вы можете пользоваться всеми функциями бота."
        )
        await state.clear()
        await show_main_menu(message)
    else:
        await message.answer(
            "У вас не установлен username в Telegram. "
            "Пожалуйста, введите ваш username (без @):"
        )
        await state.set_state(RegistrationState.username)


@router.message(RegistrationState.username)
async def process_username(message: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    EmployeeRepository.register(
        message.from_user.id,
        user_data["name"],
        user_data["birthday"],
        message.text,
    )
    await message.answer(
        "Регистрация завершена! Теперь вы можете пользоваться всеми функциями бота."
    )
    await state.clear()
    await show_main_menu(message)
