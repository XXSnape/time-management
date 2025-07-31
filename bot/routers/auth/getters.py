from aiogram.types import User
from aiogram.utils.i18n import gettext as _


async def login_or_register(event_from_user: User, **kwargs):
    return {
        "request_text": _(
            "🔒{username}, пожалуйста, выбери вариант "
            "авторизации в зависимости от того, есть ли у тебя уже аккаунт\n"
        ).format(username=event_from_user.full_name),
        "enter_text": _("🚪Вход"),
        "register_text": _("🎯Регистрация"),
    }
