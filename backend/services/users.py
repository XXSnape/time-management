from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.users import UsersDao
from core.schemas.result import ResultSchema
from core.schemas.users import (
    CredentialsSchema,
    TokenSchema,
    UserCreateSchema,
    UserInSchema,
    UserSchema,
)

from .auth import get_access_token, hash_password, validate_password


async def create_user(
    session: AsyncSession,
    user_in: UserCreateSchema,
) -> TokenSchema:

    credentials = CredentialsSchema(
        username=user_in.username,
        password=hash_password(user_in.password),
        telegram_id=user_in.telegram_id,
    )
    dao = UsersDao(session=session)
    try:
        user = await dao.add(credentials)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже существует",
        )
    return TokenSchema(
        access_token=get_access_token(user_id=user.id)
    )


async def create_new_access_token(
    session: AsyncSession,
    user_in: UserInSchema,
) -> TokenSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный логин или пароль",
    )
    user = await UsersDao(session=session).find_one_or_none(
        UserSchema(username=user_in.username)
    )
    if not user:
        raise unauthed_exc
    if not validate_password(
        password=user_in.password,
        hashed_password=user.password,
    ):
        raise unauthed_exc
    return TokenSchema(
        access_token=get_access_token(user_id=user.id),
    )


async def verify_existence_user(
    session: AsyncSession,
    username: str,
) -> ResultSchema:
    """
    Проверяет, существует ли пользователь в базе
    """
    user = await UsersDao(session=session).find_one_or_none(
        UserSchema(username=username)
    )
    return ResultSchema(result=bool(user))
