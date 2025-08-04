from aiogram.types import (
    ErrorEvent,
    Message,
    CallbackQuery,
    TelegramObject,
)
from aiogram_dialog import DialogManager
from aiogram.utils.i18n import gettext as _

from core.commands import Commands


async def end_dialog(
    dialog_manager: DialogManager,
    event: TelegramObject,
    delete_markup: bool,
):
    if dialog_manager.has_context():
        await dialog_manager.done()
        return
    if delete_markup:
        if isinstance(event, Message):
            await event.delete_reply_markup()
        elif isinstance(event, CallbackQuery):
            await event.message.delete_reply_markup()


async def on_server_is_unavailable(
    event: ErrorEvent, dialog_manager: DialogManager
):
    delete_markup = event.exception.delete_markup
    event = event.update.event

    await event.bot.send_message(
        chat_id=event.from_user.id,
        text=_(
            "😥Извините, сервер временно недоступен. Попробуйте позже!"
        ),
    )
    await end_dialog(
        dialog_manager=dialog_manager,
        event=event,
        delete_markup=delete_markup,
    )


async def on_unauthorized(
    event: ErrorEvent, dialog_manager: DialogManager
):
    delete_markup = event.exception.delete_markup
    event = event.update.event
    await event.bot.send_message(
        chat_id=event.from_user.id,
        text=_(
            "⌛Видимо, ваша сессия устарела! "
            "Пожалуйста, войдите снова через команду /{command}"
        ).format(command=Commands.auth.name),
    )
    await end_dialog(
        dialog_manager=dialog_manager,
        event=event,
        delete_markup=delete_markup,
    )


async def on_data_is_outdated(
    event: ErrorEvent, dialog_manager: DialogManager
):
    event = event.update.event
    await event.bot.send_message(
        chat_id=event.from_user.id,
        text=_(
            "⚠️Данные кажутся устаревшими! Пожалуйста, введите команду снова"
        ).format(command=Commands.auth.name),
    )
    await end_dialog(
        dialog_manager=dialog_manager,
        event=event,
        delete_markup=True,
    )
