from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from routers.common.states import (
    CreateTaskHabitStates,
    ViewTasksHabitsStates,
)
from routers.habits.handlers import (
    start_create_habit,
    start_view_habits,
)
from routers.tasks.handlers import (
    start_create_task,
    start_view_tasks,
)

from . import getters

create_task_or_habit_dialog = Dialog(
    Window(
        Format(text="{task_or_habit_text}"),
        Button(
            text=Format(text="{task_text}"),
            id="create_task",
            on_click=start_create_task,
        ),
        Button(
            text=Format(text="{habit_text}"),
            id="create_habit",
            on_click=start_create_habit,
        ),
        getter=getters.create_task_or_habit,
        state=CreateTaskHabitStates.create_task_or_habit,
    )
)


view_tasks_or_habits_dialog = Dialog(
    Window(
        Format(text="{tasks_or_habits_text}"),
        Button(
            text=Format(text="{tasks_text}"),
            id="view_tasks",
            on_click=start_view_tasks,
        ),
        Button(
            text=Format(text="{habits_text}"),
            id="view_habits",
            on_click=start_view_habits,
        ),
        getter=getters.view_tasks_or_habits,
        state=ViewTasksHabitsStates.view_tasks_or_habits,
    )
)
