from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.dao.users import UsersDao
from core.schemas.users import SignUpSchema, CredentialsSchema, TokenSchema
from .auth import hash_password, get_access_token
from fastapi import status


async def create_user(
    session: AsyncSession,
    user_in: SignUpSchema,
) -> TokenSchema:

    credentials = CredentialsSchema(
        username=user_in.username, password=hash_password(user_in.password)
    )
    dao = UsersDao(session=session)
    try:
        user = await dao.add(credentials)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже существует",
        )
    return TokenSchema(access_token=get_access_token(user_id=user.id))
