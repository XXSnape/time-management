from aiogram.fsm.state import State, StatesGroup


class CreateTaskHabitStates(StatesGroup):
    create_task_or_habit = State()


class ViewTasksHabitsStates(StatesGroup):
    view_tasks_or_habits = State()
