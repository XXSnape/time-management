from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Next,
    Button,
    Cancel,
    Calendar,
)
from aiogram_dialog.widgets.text import Format
from . import getters
from . import handlers
from .states import CreateTaskStates
from routers.common.handlers import back_to_selection

create_task_dialog = Dialog(
    Window(
        Format(text="{task_name}"),
        Button(
            text=Format("{back}"),
            id="back_to_selection",
            on_click=back_to_selection,
        ),
        Cancel(text=Format("{cancel}")),
        TextInput(
            id="task_name_input",
            on_success=Next(),
        ),
        getter=getters.task_name,
        state=CreateTaskStates.name,
    ),
    Window(
        Format(text="{calendar}"),
        Calendar(id="calendar", on_click=handlers.on_date_selected),
        Back(text=Format(text="{back}")),
        Cancel(text=Format("{cancel}")),
        getter=getters.task_date,
        state=CreateTaskStates.date,
    ),
)
