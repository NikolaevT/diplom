from aiogram.fsm.state import State, StatesGroup


class AppointmentRescheduleStates(StatesGroup):
    """Состояния FSM для переноса собеседования."""

    waiting_reason = State()
    waiting_new_date = State()
