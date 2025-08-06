from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from core.commands import Commands
from core.schemas.users import UserTelegramIdSchema
from database.dao.users import UsersDAO


async def check_user_in_database(
    message: Message,
    session: AsyncSession,
):
    if (
        await UsersDAO(session=session).find_one_or_none(
            UserTelegramIdSchema(telegram_id=message.from_user.id),
        )
        is None
    ):
        await message.answer(
            _(
                "🪪Пожалуйста, сначала пройдите регистрацию /{command}"
            ).format(command=Commands.auth.name)
        )
        return False
    return True
