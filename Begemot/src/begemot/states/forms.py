from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    feedback = State()
    wishlist_item = State()
    wishlist_remove = State()
    add_employee = State()
    remove_employee = State()


class RegistrationState(StatesGroup):
    name = State()
    birthday = State()
    username = State()
