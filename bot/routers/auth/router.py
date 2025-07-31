from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from core.commands import Commands
from routers.auth.states import AuthState

router = Router(name=__name__)


@router.message(Command(Commands.auth.name))
async def auth_handle(
    message: Message,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        state=AuthState.login_or_registration,
        mode=StartMode.RESET_STACK,
    )
