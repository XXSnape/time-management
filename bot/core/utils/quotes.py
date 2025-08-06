import logging

from httpx import AsyncClient

from core.config import settings
from core.enums import Languages

logger = logging.getLogger(__name__)


async def get_ru_and_en_quotes(
    client: AsyncClient,
) -> dict[Languages, str | None]:
    ru_quote = None
    en_quote = None
    try:
        ru_result = await client.get(
            settings.quotes.ru_api,
            params={
                "format": "json",
                "method": "getQuote",
                "lang": "ru",
            },
        )
        ru_quote = ru_result.json()["quoteText"]
    except Exception:
        logger.exception("Не удалось получить цитату на русском")
    try:
        en_result = await client.get(
            settings.quotes.en_api,
            params={"category": "motivational"},
        )
        en_quote = en_result.json()["quote"]

    except Exception:
        logger.exception("Не удалось получить цитату на английском")
    return {Languages.ru: ru_quote, Languages.en: en_quote}


def add_motivation(
    language: Languages, motivation: str | None, result: str
):
    if not motivation:
        return result
    if language == Languages.ru:
        result = (
            f"{result}\n\n\n💬Мотивационная цитата: {motivation}"
        )
    else:
        result = f"{result}\n\n\n💬Motivational quote: {motivation}"
    return result
