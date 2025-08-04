from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from core.commands import Commands
from routers.languages.states import LanguagesStates

router = Router(name=__name__)


@router.message(Command(Commands.lang.name))
async def change_language(
    message: Message,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        state=LanguagesStates.change,
        mode=StartMode.RESET_STACK,
    )
