from aiogram.types import User
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager

from core.schemas.users import UserTelegramIdSchema
from database.dao.users import UsersDAO


async def auth(
    event_from_user: User,
    dialog_manager: DialogManager,
    **kwargs,
):
    session = dialog_manager.middleware_data[
        "session_without_commit"
    ]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(telegram_id=event_from_user.id)
    )
    return {
        "request_text": _(
            "🔒{username}, пожалуйста, выбери вариант "
            "авторизации в зависимости от того, есть ли у тебя уже аккаунт\n"
        ).format(username=event_from_user.full_name),
        "register_text": _("🎯Регистрация"),
        "update_session_text": _("🔄Обновить сессию"),
        "is_logged_in": bool(user),
        "is_not_logged_in": not bool(user),
    }


async def enter_username(**kwargs):
    return {"text": _("Пожалуйста введите логин")}


async def enter_password(**kwargs):
    return {
        "text": _("Пожалуйста введите пароль"),
        "back": _("Исправить логин"),
    }
