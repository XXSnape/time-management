import logging
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from core.enums import Languages
from database.dao.base import BaseDAO
from database.models import User

logger = logging.getLogger(__name__)


class UsersDAO(BaseDAO[User]):
    model = User

    async def get_user_locale_by_telegram_id(
        self, telegram_id: int
    ) -> Languages:
        query = select(self.model.language).where(
            self.model.telegram_id == telegram_id
        )
        try:
            result = await self._session.execute(query)
            return result.scalar_one_or_none() or Languages.ru
        except SQLAlchemyError:
            logger.exception(
                "Не удалось получить язык для пользователя %s",
                telegram_id,
            )
            return Languages.ru

    async def get_user_locales(self, ids: Iterable[int]):
        query = select(
            self.model.telegram_id, self.model.language
        ).where(self.model.telegram_id.in_(ids))
        try:
            result = await self._session.execute(query)
            return result.all()
        except SQLAlchemyError:
            logger.exception(
                "Не удалось получить языки для пользователей %s",
                ids,
            )
            return []
