from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from routers.common.states import TaskHabitStates


async def back_to_selection(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        TaskHabitStates.create_task_or_habit,
        mode=StartMode.RESET_STACK,
    )


def is_short_text(max_length: int):
    def _wrapper(text: str) -> str:
        if len(text) > max_length:
            raise ValueError(max_length)
        return text

    return _wrapper


async def on_incorrect_text(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.answer(
        _(
            "Текст должен быть не длиннее {max_length} символов"
        ).format(max_length=str(error))
    )
