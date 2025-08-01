import operator
from operator import itemgetter

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Calendar,
    Group,
    Select,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Format, Const

from core.config import settings
from . import getters
from . import handlers
from .states import CreateTaskStates, ViewTaskStates
from routers.common.handlers import (
    back_to_selection,
    is_short_text,
    on_incorrect_text,
    save_text_by_key,
)

create_task_dialog = Dialog(
    Window(
        Format(text="{task_name}"),
        Button(
            text=Format("{back}"),
            id="back_to_selection",
            on_click=back_to_selection,
        ),
        TextInput(
            id="task_name_input",
            type_factory=is_short_text(
                max_length=settings.bot.max_name_length,
            ),
            on_success=save_text_by_key(key="name"),
            on_error=on_incorrect_text,
        ),
        getter=getters.task_name,
        state=CreateTaskStates.name,
    ),
    Window(
        Format(text="{task_description}"),
        Back(text=Format(text="{back}")),
        TextInput(
            id="task_description_input",
            type_factory=is_short_text(
                max_length=settings.bot.max_description_length,
            ),
            on_success=save_text_by_key(key="description"),
            on_error=on_incorrect_text,
        ),
        getter=getters.task_description,
        state=CreateTaskStates.description,
    ),
    Window(
        Format(text="{calendar}"),
        Calendar(id="calendar", on_click=handlers.on_date_selected),
        Back(text=Format(text="{back}")),
        getter=getters.task_date,
        state=CreateTaskStates.date,
    ),
    Window(
        Format(text="{hour_text}"),
        Group(
            Select(
                Format("{item[0]}"),
                id="hour",
                item_id_getter=itemgetter(1),
                items="hours",
                on_click=handlers.save_hour,
            ),
            width=2,
        ),
        Back(text=Format(text="{back}")),
        getter=getters.task_hour,
        state=CreateTaskStates.hour,
    ),
    Window(
        Format(text="{notification_hour_text}"),
        Group(
            Select(
                Format("{item[0]}"),
                id="hour",
                item_id_getter=itemgetter(1),
                items="hours",
                on_click=handlers.save_task,
            ),
            width=2,
        ),
        Back(text=Format(text="{back}")),
        getter=getters.task_notification_hour,
        state=CreateTaskStates.notification_hour,
    ),
)


view_tasks_dialog = Dialog(
    Window(
        Format(text="{tasks_text}"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="tasks",
                item_id_getter=operator.itemgetter(1),
                items="tasks",
            ),
            id="all_tasks",
            width=1,
            height=5,
        ),
        Button(
            Format(text="{load_more}"),
            id="load_tasks",
            when="can_be_loaded",
            on_click=handlers.upload_more_tasks,
        ),
        state=ViewTaskStates.view_all,
        getter=getters.get_user_tasks,
    )
)
