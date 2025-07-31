from httpx import (
    AsyncClient,
    RequestError,
    Request,
    codes,
    HTTPStatusError,
)

from core.config import settings
from core.enums import Methods
from core.exc import UnauthorizedExc, ServerIsUnavailable
import logging

logger = logging.getLogger(__name__)


async def make_request(
    client: AsyncClient,
    endpoint: str,
    method: Methods,
    json: dict | None = None,
    access_token: str | None = None,
    params: dict | None = None,
) -> dict | None:
    cookies = None
    if access_token:
        cookies = {"access-token": access_token}
    try:
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
            raise UnauthorizedExc
        try:
            response.raise_for_status()
        except HTTPStatusError:
            logger.exception("Ошибка при запросе к серверу")
            raise ServerIsUnavailable
        if response.status_code == codes.NO_CONTENT:
            return None
        return response.json()
    except RequestError:
        logger.exception("Ошибка при запросе к серверу")
        raise ServerIsUnavailable
