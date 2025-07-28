import logging

from fastapi import APIRouter

from core.dependencies.db import SessionWithCommit
from core.schemas.users import SignUpSchema, TokenSchema
from services.users import create_user
from fastapi import status


log = logging.getLogger(__name__)


router = APIRouter(tags=["Пользователи"])


@router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenSchema,
)
async def sign_up(
    credentials: SignUpSchema,
    session: SessionWithCommit,
):
    return await create_user(
        session=session,
        user_in=credentials,
    )
