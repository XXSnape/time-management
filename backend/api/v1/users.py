import logging

from fastapi import APIRouter, status

from core.dependencies.db import (
    SessionWithCommit,
    SessionWithoutCommit,
)
from core.schemas.result import ResultSchema
from core.schemas.users import (
    TokenSchema,
    UserActivitySchema,
    UserCreateSchema,
    UserInSchema,
)
from services import users

log = logging.getLogger(__name__)


router = APIRouter(tags=["Пользователи"])


@router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenSchema,
)
async def sign_up(
    user_in: UserCreateSchema,
    session: SessionWithCommit,
):
    return await users.create_user(
        session=session,
        user_in=user_in,
    )


@router.post(
    "/sign-in",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenSchema,
)
async def sign_in(
    user_in: UserInSchema,
    session: SessionWithoutCommit,
):
    """
    Роутер для перевыпуска токена
    """
    return await users.create_new_access_token(
        session=session,
        user_in=user_in,
    )


@router.get("/{username}", response_model=ResultSchema)
async def check_username_for_existence(
    username: str,
    session: SessionWithoutCommit,
):
    return await users.verify_existence_user(
        username=username,
        session=session,
    )


@router.patch(
    "/{telegram_id}",
    response_model=ResultSchema,
)
async def change_activity(
    user_activity: UserActivitySchema,
    telegram_id: int,
    session: SessionWithCommit,
):
    return await users.make_user_inactive_or_active(
        telegram_id=telegram_id,
        session=session,
        user_activity=user_activity,
    )
