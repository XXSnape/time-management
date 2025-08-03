import logging

from httpx import AsyncClient

from core.enums import Languages

logger = logging.getLogger(__name__)


async def get_ru_and_en_quotes(
    client: AsyncClient,
) -> dict[str, str | None]:
    ru_quote = None
    en_quote = None
    try:
        ru_result = await client.get(
            "http://api.forismatic.com/api/1.0/",
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
            "https://quote-generator-api-six.vercel.app/api/quotes/random",
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
        result = f"{result}\n\n\nМотивационная цитата: {motivation}"
    else:
        result = f"{result}\n\n\nMotivational quote: {motivation}"
    return result
