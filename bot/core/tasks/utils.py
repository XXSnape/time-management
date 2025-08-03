import logging

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import Languages
from core.utils.dt import get_pretty_dt
from database.dao.users import UsersDAO


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


def translate_task(
    language: Languages,
    name: str,
    deadline: str,
    motivation: str | None,
) -> str:
    moscow_dt = get_pretty_dt(deadline)
    if language == Languages.ru:
        result = (
            "Напоминание о задаче:\n\n"
            f"Название: {name}\n\n"
            f"Дата и время дедлайна: {moscow_dt}"
        )
    else:
        result = (
            "Reminder about the task:\n\n"
            f"Title: {name}\n\n"
            f"Deadline date and time: {moscow_dt}"
        )
    return add_motivation(
        language=language, motivation=motivation, result=result
    )


def translate_habit(
    language: Languages,
    name: str,
    motivation: str | None,
) -> str:
    if language == Languages.ru:
        result = "Напоминание о привычке:\n\n" f"Название: {name}"
    else:
        result = "Reminder about the habit:\n\n" f"Title: {name}"
    return add_motivation(
        language=language, motivation=motivation, result=result
    )


async def get_users_locales(
    items: list[dict], session: AsyncSession
):
    users = set(item["user"]["telegram_id"] for item in items)
    user_with_locale = await UsersDAO(
        session=session
    ).get_user_locales(users)
    user_and_locale = {
        telegram_id: locale
        for telegram_id, locale in user_with_locale
    }
    return user_and_locale
