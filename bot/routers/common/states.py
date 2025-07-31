from aiogram.fsm.state import StatesGroup, State


class TaskHabitStates(StatesGroup):
    create_task_or_habit = State()
