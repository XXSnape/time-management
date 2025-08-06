import logging

from httpx import (
    AsyncClient,
    HTTPStatusError,
    Request,
    RequestError,
    codes,
)

from core.config import redis, settings
from core.enums import Methods
from core.exc import ServerIsUnavailableExc, UnauthorizedExc

logger = logging.getLogger(__name__)


async def make_request(
    client: AsyncClient,
    endpoint: str,
    method: Methods,
    json: dict | None = None,
    access_token: str | None = None,
    params: dict | None = None,
    delete_markup: bool = True,
) -> dict | None:
    cookies = None
    if access_token:
        cookies = {"access-token": access_token}
    try:
        url = settings.api.get_url(endpoint)
        print("url", url)
        response = await client.send(
            request=Request(
                method=method,
                url=settings.api.get_url(endpoint),
                params=params,
                cookies=cookies,
                json=json,
            )
        )
        if response.status_code in (
            codes.UNAUTHORIZED,
            codes.FORBIDDEN,
        ):
            raise UnauthorizedExc(delete_markup=delete_markup)
        try:
            response.raise_for_status()
        except HTTPStatusError as e:
            logger.exception("Ошибка при запросе к серверу")
            raise ServerIsUnavailableExc(
                response=e.response, delete_markup=delete_markup
            )
        return response.json()
    except RequestError:
        logger.exception("Ошибка при запросе к серверу")
        raise ServerIsUnavailableExc(delete_markup=delete_markup)


async def set_new_admin_token(
    client: AsyncClient,
) -> str:
    """
    Получает токен администратора.
    """
    try:
        response = await make_request(
            client=client,
            endpoint="users/sign-in",
            method=Methods.post,
            json={
                "username": settings.bot.login,
                "password": settings.bot.password,
            },
        )
        access_token = response["access_token"]
        await redis.set(settings.bot.access_token, access_token)
        return access_token
    except UnauthorizedExc:
        logger.exception(
            "Неверный логин или пароль администратора. Проверьте настройки."
        )
        raise ServerIsUnavailableExc


async def make_request_by_admin(
    client: AsyncClient,
    endpoint: str,
    method: Methods,
    json: dict | None = None,
    params: dict | None = None,
    delete_markup: bool = True,
) -> dict | None:
    """
    Выполняет запрос к серверу от имени администратора.
    """
    access_token = await redis.get(settings.bot.access_token)
    if not access_token:
        access_token = await set_new_admin_token(client)
    data = dict(
        client=client,
        endpoint=endpoint,
        method=method,
        json=json,
        access_token=access_token,
        params=params,
        delete_markup=delete_markup,
    )
    try:
        return await make_request(**data)
    except UnauthorizedExc:
        logger.warning(
            "Токен администратора устарел или недействителен. "
            "Попытка обновления токена."
        )
        access_token = await set_new_admin_token(client)
        data["access_token"] = access_token
        return await make_request(**data)
