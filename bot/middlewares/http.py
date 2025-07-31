from aiogram import BaseMiddleware
from httpx import AsyncClient


class HttpClientMiddleware(BaseMiddleware):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def __call__(self, handler, event, data):
        data["client"] = self.client
        return await handler(event, data)
