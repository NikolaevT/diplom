from aiogram.fsm.state import State, StatesGroup


class TaskCreationStates(StatesGroup):
    """
    Состояния FSM для создания задачи в Jira.
    """

    # Ожидание выбора проекта
    waiting_project_selection = State()
    # Ожидание выбора проекта (в групповом чате)
    waiting_group_project_selection = State()
    # Ожидание выбора темы (для группового чата)
    waiting_topic_selection = State()
    # Ожидание текста задачи
    waiting_task_text = State()
    # Ожидание подтверждения создания задачи
    waiting_task_confirmation = State()
