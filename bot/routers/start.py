from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.utils.start_text import get_start_text

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start_process(message: Message):
    await message.answer(get_start_text(message.from_user))
