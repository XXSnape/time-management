from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start_process(message: Message):
    await message.answer(
        _(
            "Здравствуйте, {name}!\n\n"
            "Это бот для помощи отслеживания задач и привычек!"
        ).format(name=message.from_user.full_name)
    )
