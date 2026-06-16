from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.begemot.handlers.menu import show_main_menu
from src.begemot.repository.employee_repository import EmployeeRepository
from src.begemot.states.forms import RegistrationState

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    if EmployeeRepository.exists(user_id):
        await message.answer("Привет! Я бот-бегемот от команды БМК. Выбери нужную функцию:")
        await show_main_menu(message)
    else:
        await message.answer(
            "Добро пожаловать! Похоже, вы новый сотрудник. "
            "Давайте зарегистрируем вас в системе.\n\n"
            "Пожалуйста, введите ваше имя и фамилию:",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.set_state(RegistrationState.name)
