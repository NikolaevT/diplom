from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Состояния анкеты кандидата."""

    waiting_full_name = State()
    waiting_birth_date = State()
    waiting_email = State()
