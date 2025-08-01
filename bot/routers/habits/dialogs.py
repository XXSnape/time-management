from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
)
from aiogram_dialog.widgets.text import Format

from core.config import settings
from . import getters
from .states import CreateHabitStates
from routers.common.handlers import (
    back_to_selection,
    is_short_text,
    on_incorrect_text,
    save_text_by_key,
)

create_habit_dialog = Dialog(
    Window(
        Format(text="{habit_name}"),
        Button(
            text=Format("{back}"),
            id="back_to_selection",
            on_click=back_to_selection,
        ),
        TextInput(
            id="habit_name_input",
            type_factory=is_short_text(
                max_length=settings.bot.max_name_length,
            ),
            on_success=save_text_by_key(key="name"),
            on_error=on_incorrect_text,
        ),
        getter=getters.habit_name,
        state=CreateHabitStates.name,
    ),
    Window(
        Format(text="{habit_purpose}"),
        Back(text=Format(text="{back}")),
        TextInput(
            id="habit_purpose_input",
            type_factory=is_short_text(
                max_length=settings.bot.max_description_length,
            ),
            on_success=save_text_by_key(key="purpose"),
            on_error=on_incorrect_text,
        ),
        getter=getters.habit_purpose,
        state=CreateHabitStates.purpose,
    ),
)
