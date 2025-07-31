from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

import routers.tasks.handlers
from routers.common.states import TaskHabitStates
from . import getters

create_task_or_habit_dialog = Dialog(
    Window(
        Format(text="{task_or_habit_text}"),
        Button(
            text=Format(text="{task_text}"),
            id="create_task",
            on_click=routers.tasks.handlers.start_create_task,
        ),
        Button(text=Format(text="{habit_text}"), id="create_habit"),
        getter=getters.create_task_or_habit,
        state=TaskHabitStates.create_task_or_habit,
    )
)
