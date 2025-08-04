from aiogram.types import InlineKeyboardButton

from .common import generate_inline_kb

from aiogram.filters.callback_data import CallbackData

from core.enums import Languages


class TaskCbData(CallbackData, prefix="task_completed"):
    task_id: int


def complete_task_kb(task_id: int, language: Languages):
    if language == Languages.ru:
        text = "🚩Отметить выполненной"
    else:
        text = "🚩Mark Completed"
    return generate_inline_kb(
        [
            InlineKeyboardButton(
                text=text,
                callback_data=TaskCbData(task_id=task_id).pack(),
            )
        ],
    )
