from aiogram.fsm.state import StatesGroup, State


class StatsTasksHabitsStates(StatesGroup):
    stats_tasks_or_habits = State()
    text_or_file = State()
    text = State()
