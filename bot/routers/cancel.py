from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from core.commands import Commands

router = Router(name=__name__)


@router.message(Command(Commands.cancel.name))
async def cancel_dialog(
    message: Message,
    dialog_manager: DialogManager,
):
    await message.delete()
    await dialog_manager.done()
