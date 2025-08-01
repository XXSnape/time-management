from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from routers.common.states import TaskHabitStates
from . import getters
from routers.habits.handlers import start_create_habit
from routers.tasks.handlers import start_create_task

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
        state=TaskHabitStates.create_task_or_habit,
    )
)
