import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.users import UsersDao
from core.dependencies.db import db_helper
from core.schemas import users as users_schemas
from core.schemas.result import ResultSchema

from .auth import get_access_token, hash_password, validate_password

logger = logging.getLogger(__name__)


async def create_user(
    session: AsyncSession,
    user_in: users_schemas.UserCreateSchema,
    is_admin: bool = False,
) -> users_schemas.TokenSchema:

    credentials = users_schemas.CredentialsSchema(
        username=user_in.username,
        password=hash_password(user_in.password),
        telegram_id=user_in.telegram_id,
        is_admin=is_admin,
    )
    dao = UsersDao(session=session)
    try:
        user = await dao.add(credentials)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже существует",
        )
    return users_schemas.TokenSchema(
        access_token=get_access_token(
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin,
        )
    )


async def create_new_access_token(
    session: AsyncSession,
    user_in: users_schemas.UserInSchema,
) -> users_schemas.TokenSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный логин или пароль",
    )
    user = await UsersDao(session=session).find_one_or_none(
        users_schemas.UserSchema(username=user_in.username)
    )
    if not user:
        raise unauthed_exc
    if not validate_password(
        password=user_in.password,
        hashed_password=user.password,
    ):
        raise unauthed_exc
    return users_schemas.TokenSchema(
        access_token=get_access_token(
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin,
        ),
    )


async def verify_existence_user(
    session: AsyncSession,
    username: str,
) -> ResultSchema:
    """
    Проверяет, существует ли пользователь в базе
    """
    user = await UsersDao(session=session).find_one_or_none(
        users_schemas.UserSchema(username=username)
    )
    return ResultSchema(result=bool(user))


async def make_user_inactive_or_active(
    telegram_id: int,
    session: AsyncSession,
    user_activity: users_schemas.UserActivitySchema,
) -> ResultSchema:
    result = await UsersDao(session=session).update(
        filters=users_schemas.UserTelegramIdSchema(
            telegram_id=telegram_id
        ),
        values=user_activity,
    )
    if result == 0:
        raise HTTPException(
            detail="Пользователь не найден",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return ResultSchema()


async def create_admin(
    username: str,
    password: str,
    telegram_id: int,
) -> None:
    async with db_helper.session_factory() as session:
        try:
            await create_user(
                session=session,
                user_in=users_schemas.UserCreateSchema(
                    username=username,
                    password=password,
                    telegram_id=telegram_id,
                ),
                is_admin=True,
            )
            await session.commit()
            logger.info("Админ %s успешно создан", username)
        except HTTPException:
            await session.rollback()
            logger.info("Админ %s уже существует", username)
