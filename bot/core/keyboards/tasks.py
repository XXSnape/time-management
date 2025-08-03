from aiogram.types import InlineKeyboardButton

from .common import generate_inline_kb

from aiogram.filters.callback_data import CallbackData


class TaskCbData(CallbackData, prefix="task_completed"):
    task_id: int


def complete_task_kb(task_id: int, text: str):
    return generate_inline_kb(
        [
            InlineKeyboardButton(
                text=text,
                callback_data=TaskCbData(task_id=task_id).pack(),
            )
        ],
    )
