from aiogram.fsm.state import State, StatesGroup


class StatsTasksHabitsStates(StatesGroup):
    stats_tasks_or_habits = State()
    text_or_file = State()
    text = State()
