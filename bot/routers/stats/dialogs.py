from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Back, SwitchTo
from aiogram_dialog.widgets.text import Format

from .states import StatsTasksHabitsStates
from . import getters, handlers


stats_tasks_or_habits_dialog = Dialog(
    Window(
        Format(text="{tasks_or_habits_text}"),
        Button(
            text=Format(text="{tasks_text}"),
            id="stats_tasks",
            on_click=handlers.choosing_statistics("tasks"),
        ),
        Button(
            text=Format(text="{habits_text}"),
            id="stats_habits",
            on_click=handlers.choosing_statistics("habits"),
        ),
        state=StatsTasksHabitsStates.stats_tasks_or_habits,
        getter=getters.stats_tasks_or_habits,
    ),
    Window(
        Format(text="{text_or_file}"),
        Button(
            text=Format(text="{text}"),
            id="stats_text",
            on_click=handlers.get_stats_by_text,
        ),
        Button(
            text=Format(text="{file}"),
            id="stats_file",
            on_click=handlers.get_stats_by_file,
        ),
        Back(text=Format(text="{back}"), id="stats_back"),
        state=StatsTasksHabitsStates.text_or_file,
        getter=getters.text_or_file,
    ),
)
