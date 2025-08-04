from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from . import getters, handlers
from .states import ActivityStates

change_activity_dialog = Dialog(
    Window(
        Format(text="{text}"),
        Button(
            text=Format("{activate_text}"),
            id="activate_bot",
            on_click=handlers.activate_or_deactivate_bot(
                is_active=True
            ),
        ),
        Button(
            text=Format("{deactivate_text}"),
            id="deactivate_bot",
            on_click=handlers.activate_or_deactivate_bot(
                is_active=False
            ),
        ),
        state=ActivityStates.change,
        getter=getters.change_activity,
    )
)
