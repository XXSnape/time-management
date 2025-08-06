import logging

from core.config import settings
from core.dao.users import UsersDao
from core.dependencies.db import db_helper
from core.schemas.users import UserSchema
from jwt import InvalidTokenError
from services.auth import (
    decode_jwt,
    get_access_token,
    validate_password,
)
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    async def login(
        self,
        request: Request,
    ) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        async with db_helper.session_factory() as session:
            user = await UsersDao(session=session).find_one_or_none(
                UserSchema(username=username)
            )
            print("user", user)
            if (
                not user
                or not validate_password(
                    password=password, hashed_password=user.password
                )
                or not user.is_admin
            ):
                logger.warning(
                    "Попытка войти в административную панель не удалась. Пользователь - %s",
                    username,
                )
                return False
            token = get_access_token(
                user_id=user.id,
                username=username,
                is_admin=user.is_admin,
            )
            request.session.update(
                {settings.auth_jwt.cookie_key_token: token}
            )
            logger.info(
                "Выполнен вход в административную панель пользователем %s",
                username,
            )

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        logger.info("Выполнен выход их административной панели")
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get(
            settings.auth_jwt.cookie_key_token
        )
        if not token:
            logger.warning(
                "Попытка войти в административную панель без токена"
            )
            return False
        try:
            payload = decode_jwt(
                token=token,
            )
            if bool(payload["is_admin"]):
                logger.info(
                    "Выполнен вход в административную панель пользователем %s",
                    payload["username"],
                )
                return True
            logger.warning(
                "Попытка войти в административную панель не от админа пользователем %s",
                payload["username"],
            )
            return False
        except InvalidTokenError as e:
            logger.info(
                "Попытка войти в административную панель с невалидным токеном %s",
                token,
            )
            return False
