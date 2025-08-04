from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from core.commands import Commands
from routers.activity.states import ActivityStates

router = Router(name=__name__)


@router.message(Command(Commands.activity.name))
async def change_activity(
    message: Message,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        state=ActivityStates.change,
        mode=StartMode.RESET_STACK,
    )
