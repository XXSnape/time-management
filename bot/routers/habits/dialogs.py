import operator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Column,
    Multiselect,
    Group,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Format

from core.config import settings
from . import getters, handlers
from .states import CreateHabitStates, HabitsManagementStates
from routers.common.handlers import (
    back_to_selection,
    is_short_text,
    on_incorrect_text,
    save_text_by_key,
    on_click_habit,
    upload_habits,
    delete_habit,
)

from routers.common.getters import get_habits, get_item_details

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
    Window(
        Format(text="{days_text}"),
        Column(
            Multiselect(
                checked_text=Format("[✅] {item[0]}"),
                unchecked_text=Format("[  ] {item[0]}"),
                id="multi_days",
                item_id_getter=operator.itemgetter(1),
                items="days",
                min_selected=1,
            ),
        ),
        Button(
            text=Format(text="{save_text}"),
            when="can_be_saved",
            on_click=handlers.save_checkbox,
            id="save_days",
        ),
        Back(text=Format(text="{back}")),
        state=CreateHabitStates.days,
        getter=getters.get_days_of_week,
    ),
    Window(
        Format(text="{hours_text}"),
        Group(
            Multiselect(
                checked_text=Format("[✅] {item[0]}"),
                unchecked_text=Format("[  ] {item[0]}"),
                id="multi_hours",
                item_id_getter=operator.itemgetter(1),
                items="hours",
                min_selected=1,
            ),
            width=2,
        ),
        Button(
            text=Format(text="{save_text}"),
            when="can_be_saved",
            on_click=handlers.save_habit,
            id="save_hours",
        ),
        Back(text=Format(text="{back}")),
        state=CreateHabitStates.hours,
        getter=getters.get_hours,
    ),
)


habits_management_dialog = Dialog(
    Window(
        Format(text="{items_text}"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="habit",
                item_id_getter=operator.itemgetter(1),
                items="items",
                on_click=on_click_habit,
            ),
            id="all_habits",
            width=1,
            height=5,
        ),
        Button(
            Format(text="{load_more}"),
            id="load_habits",
            when="can_be_loaded",
            on_click=upload_habits,
        ),
        state=HabitsManagementStates.view_all,
        getter=get_habits,
    ),
    Window(
        Format(text="{item_text}"),
        Back(text=Format(text="{back}")),
        # SwitchTo(
        #     text=Format(text="{edit_text}"),
        #     id="edit_task",
        #     state=TasksManagementStates.edit_task,
        # ),
        SwitchTo(
            text=Format(text="{delete_text}"),
            id="delete_habit",
            state=HabitsManagementStates.delete_habit,
        ),
        state=HabitsManagementStates.view_details,
        getter=get_item_details,
    ),
    Window(
        Format(text="{confirm_text}"),
        Button(
            text=Format(text="{confirm_delete_habit_text}"),
            id="confirm_delete_habit",
            on_click=delete_habit,
        ),
        SwitchTo(
            text=Format(text="{back}"),
            id="cancel_habit_deletion",
            state=HabitsManagementStates.view_details,
        ),
        state=HabitsManagementStates.delete_habit,
        getter=getters.delete_habit,
    ),
)
