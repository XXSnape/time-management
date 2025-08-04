from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from core.commands import Commands
from core.utils.db import check_user_in_database
from routers.languages.states import LanguagesStates

router = Router(name=__name__)


@router.message(Command(Commands.lang.name))
async def change_language(
    message: Message,
    dialog_manager: DialogManager,
    session_without_commit: AsyncSession,
):
    if await check_user_in_database(
        message=message, session=session_without_commit
    ):
        await dialog_manager.start(
            state=LanguagesStates.change,
            mode=StartMode.RESET_STACK,
        )
