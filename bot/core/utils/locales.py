from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.users import UsersDAO


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
