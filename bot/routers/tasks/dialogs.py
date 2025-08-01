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
    Next,
    SwitchTo,
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
                on_click=handlers.on_click_task,
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
    ),
    Window(
        Format(text="{task_text}"),
        Back(text=Format(text="{back}")),
        SwitchTo(
            text=Format(text="{edit_text}"),
            id="edit_task",
            state=ViewTaskStates.edit_task,
        ),
        SwitchTo(
            text=Format(text="{delete_text}"),
            id="delete_task",
            state=ViewTaskStates.delete_task,
        ),
        state=ViewTaskStates.view_details,
        getter=getters.get_task_details,
    ),
    Window(
        Format(text="{confirm_text}"),
        Button(
            text=Format(text="{confirm_delete_task_text}"),
            id="confirm_delete_task",
            on_click=handlers.delete_task,
        ),
        SwitchTo(
            text=Format(text="{back}"),
            id="cancel_task_deletion",
            state=ViewTaskStates.view_details,
        ),
        state=ViewTaskStates.delete_task,
        getter=getters.delete_task,
    ),
    Window(
        Format(text="{task_text}"),
        SwitchTo(
            text=Format(text="{name}"),
            id="change_name",
            state=ViewTaskStates.edit_name,
        ),
        # Button(
        #     text=Format(text="{name}"),
        #     id="change_name",
        #     on_click=handlers.change_name,
        # ),
        Button(
            text=Format(text="{description_text}"),
            id="change_description_text",
        ),
        Button(
            text=Format(text="{deadline_date_text}"),
            id="change_deadline_date_text",
        ),
        Button(
            text=Format(text="{deadline_time_text}"),
            id="change_deadline_time_text",
        ),
        Button(
            text=Format(text="{notification_hour_text}"),
            id="change_notification_hour_text",
        ),
        Button(
            text=Format(text="{mark_text}"),
            id="change_mark_text",
        ),
        SwitchTo(
            text=Format(text="{back}"),
            id="cancel_task_edition",
            state=ViewTaskStates.view_details,
        ),
        state=ViewTaskStates.edit_task,
        getter=getters.edit_task,
    ),
    Window(
        Format(text="{task_name}"),
        SwitchTo(
            text=Format("{back}"),
            id="cancel_edit_name",
            state=ViewTaskStates.edit_task,
        ),
        # Button(
        #     text=Format("{back}"),
        #     id="back_to_selection",
        #     on_click=back_to_selection,
        # ),
        TextInput(
            id="change_task_name",
            type_factory=is_short_text(
                max_length=settings.bot.max_name_length,
            ),
            on_success=handlers.change_name,
            on_error=on_incorrect_text,
        ),
        getter=getters.edit_task_name,
        state=ViewTaskStates.edit_name,
    ),
)
