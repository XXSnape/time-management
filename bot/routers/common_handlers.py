from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager
from aiogram.utils.i18n import gettext as _


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
    await dialog_manager.done()
