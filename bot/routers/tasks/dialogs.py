from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Next,
    SwitchTo,
    Button,
    Cancel,
)
from aiogram_dialog.widgets.text import Format, Const
from . import getters
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
        Const("hello"),
        # Back(text=Format(text="{back}")),
        # TextInput(
        #     id="task_name_input",
        #     on_success=Next(),
        # ),
        # getter=getters.task_name,
        state=CreateTaskStates.date,
    ),
)
