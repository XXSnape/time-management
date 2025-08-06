from collections.abc import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_inline_kb(
    data_with_buttons: Iterable[InlineKeyboardButton] = (),
    sizes: Iterable[int] = (1,),
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for data in data_with_buttons:
        if data:
            builder.add(data)
    builder.adjust(*sizes)
    return builder.as_markup()
