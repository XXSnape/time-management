import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.dao.base import BaseDAO
from database.models import User
from core.enums import Languages

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
