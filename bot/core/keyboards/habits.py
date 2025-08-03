from aiogram.types import InlineKeyboardButton

from .common import generate_inline_kb

from aiogram.filters.callback_data import CallbackData

from core.enums import Languages, Weekday


class HabitCbData(CallbackData, prefix="habit_execution"):
    habit_id: int
    completed: bool
    date: str
    hour: int


def completed_or_not_completed_habit_kb(
    habit_id: int,
    language: Languages,
    date: str,
    hour: int,
):

    if language == Languages.ru:
        completed_text = "Отметить выполненной"
        not_completed_text = "Отметить невыполненной"
    else:
        completed_text = "Mark Completed"
        not_completed_text = "Mark as unfulfilled"
    completed_cb_data = HabitCbData(
        habit_id=habit_id, date=date, hour=hour, completed=True
    )
    not_completed_cb_data = completed_cb_data.model_copy(
        update={"completed": False}
    )
    return generate_inline_kb(
        [
            InlineKeyboardButton(
                text=completed_text,
                callback_data=completed_cb_data.pack(),
            ),
            InlineKeyboardButton(
                text=not_completed_text,
                callback_data=not_completed_cb_data.pack(),
            ),
        ],
    )
