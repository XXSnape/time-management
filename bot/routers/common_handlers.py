import logging

from aiogram.types import (
    CallbackQuery,
    ErrorEvent,
    Message,
    TelegramObject,
)
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager

from core.commands import Commands
from core.utils.start_text import get_start_text

logger = logging.getLogger(__name__)


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


async def on_unknown_intent(event, dialog_manager: DialogManager):
    logger.error("Перезапускаем диалог: %s", event.exception)
    event = event.update.event
    await event.bot.send_message(
        chat_id=event.from_user.id,
        text=get_start_text(event.from_user),
    )
    await end_dialog(
        dialog_manager=dialog_manager,
        event=event,
        delete_markup=True,
    )


async def on_unknown_state(event, dialog_manager: DialogManager):
    logger.error("Перезапускаем диалог: %s", event.exception)
    event = event.update.event
    await event.bot.send_message(
        chat_id=event.from_user.id,
        text=get_start_text(event.from_user),
    )
    await end_dialog(
        dialog_manager=dialog_manager,
        event=event,
        delete_markup=True,
    )
