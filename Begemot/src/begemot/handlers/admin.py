from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.begemot.config.settings import settings
from src.begemot.repository.employee_repository import EmployeeRepository
from src.begemot.states.forms import Form

router = Router(name="admin")


@router.message(Command("add_employee"))
async def cmd_add_employee(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Введите данные сотрудника в формате:\n"
        "TelegramID Имя Фамилия ДД.ММ\n\n"
        "Пример: 123456789 Иван Иванов 15.05"
    )
    await state.set_state(Form.add_employee)


@router.message(Form.add_employee)
async def process_add_employee(message: types.Message, state: FSMContext) -> None:
    try:
        parts = message.text.rsplit(" ", 1)
        birthday = parts[1]
        identity = parts[0].split(" ", 1)
        user_id = int(identity[0])
        name = identity[1]
        day, month = map(int, birthday.split("."))
        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError
        username = message.from_user.username or "-"
        EmployeeRepository.add(user_id, name, birthday, username)
        await message.answer(
            f"Сотрудник успешно добавлен!\n"
            f"Telegram ID: {user_id}\n"
            f"Имя: {name}\n"
            f"Дата рождения: {birthday}\n"
            f"Username: {username}"
        )
    except (ValueError, IndexError):
        await message.answer(
            "Ошибка формата. Используйте: TelegramID Имя Фамилия ДД.ММ"
        )
    finally:
        await state.clear()


@router.message(Command("remove_employee"))
async def cmd_remove_employee(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id not in settings.admin_id_list:
        await message.answer("Эта команда доступна только администраторам.")
        return

    await message.answer("Введите имя сотрудника для удаления:")
    await state.set_state(Form.remove_employee)


@router.message(Form.remove_employee)
async def process_remove_employee(message: types.Message, state: FSMContext) -> None:
    EmployeeRepository.remove(message.text)
    await message.answer("Сотрудник успешно удален!")
    await state.clear()
