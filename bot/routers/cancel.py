from contextlib import suppress

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.api.exceptions import NoContextError

from core.commands import Commands

router = Router(name=__name__)


@router.message(Command(Commands.cancel.name))
async def cancel_dialog(
    message: Message,
    dialog_manager: DialogManager,
):
    await message.delete()
    with suppress(NoContextError):
        await dialog_manager.done()
