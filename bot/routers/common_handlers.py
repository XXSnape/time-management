from aiogram.types import (
    ErrorEvent,
    Message,
    CallbackQuery,
    TelegramObject,
)
from aiogram_dialog import DialogManager
from aiogram.utils.i18n import gettext as _

from core.commands import Commands


async def delete_markup(
    dialog_manager: DialogManager, event: TelegramObject
):
    if dialog_manager.has_context():
        await dialog_manager.done()
        return
    if isinstance(event, Message):
        await event.delete_reply_markup()
    elif isinstance(event, CallbackQuery):
        await event.message.delete_reply_markup()


async def on_server_is_unavailable(
    event: ErrorEvent, dialog_manager: DialogManager
):
    event = event.update.event
    await event.bot.send_message(
        chat_id=event.from_user.id,
        text=_(
            "Извините, сервер временно недоступен. Попробуйте позже!"
        ),
    )
    await delete_markup(dialog_manager=dialog_manager, event=event)


async def on_unauthorized(
    event: ErrorEvent, dialog_manager: DialogManager
):
    event = event.update.event
    await event.bot.send_message(
        chat_id=event.from_user.id,
        text=_(
            "Видимо, ваша сессия устарела! "
            "Пожалуйста, войдите снова через команду /{command}"
        ).format(command=Commands.auth.name),
    )
    await delete_markup(dialog_manager=dialog_manager, event=event)
