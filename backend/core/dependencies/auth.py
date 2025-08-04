from typing import Annotated, TypeAlias

from fastapi import Depends, HTTPException, status, Cookie
from jwt import InvalidTokenError

from core.schemas.users import UserForTemplateSchema
from core.utils.exc import RedirectException
from services import auth

from core.config import settings


type token_payload = dict[str, str | int]


def get_token_payload(
    token: Annotated[
        str, Cookie(alias=settings.auth_jwt.cookie_key_token)
    ],
) -> token_payload:
    """
    Декодирует токен и возвращает полезную нагрузку из него
    :param token: токен
    :return: полезная нагрузка в токене.
    """
    try:
        payload = auth.decode_jwt(
            token=token,
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error",
        )
    return payload


def get_user_id(
    payload: Annotated[dict, Depends(get_token_payload)],
) -> int:
    """
    Получает id пользователя
    :param payload: Annotated[dict, Depends(get_token_payload)])
    :return: id пользователя
    """
    return int(payload.get("sub"))


def get_user_for_template(
    token: Annotated[
        str | None, Cookie(alias=settings.auth_jwt.cookie_key_token)
    ] = None,
):
    try:
        payload = auth.decode_jwt(
            token=token,
        )
    except InvalidTokenError:
        raise RedirectException
    return UserForTemplateSchema(
        id=int(payload.get("sub")),
        username=payload.get("username"),
    )


UserId: TypeAlias = Annotated[int, Depends(get_user_id)]
UserDep: TypeAlias = Annotated[
    UserForTemplateSchema, Depends(get_user_for_template)
]
