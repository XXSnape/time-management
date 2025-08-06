from typing import Any, Dict, Optional

from aiogram.types import TelegramObject, User
from aiogram.utils.i18n import I18nMiddleware

from core.enums import Languages
from database.dao.users import UsersDAO


class LocaleFromDatabaseMiddleware(I18nMiddleware):
    async def get_locale(
        self, event: TelegramObject, data: Dict[str, Any]
    ) -> str:
        event_from_user: Optional[User] = data.get(
            "event_from_user", None
        )
        if event_from_user:
            session = data.get("session_without_commit")
            return await UsersDAO(
                session=session
            ).get_user_locale_by_telegram_id(
                telegram_id=event_from_user.id
            )
        return Languages.ru
