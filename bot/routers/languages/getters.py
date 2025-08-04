from aiogram.utils.i18n import gettext as _

from core.enums import Languages


async def choose_language(**kwargs):
    languages = [
        (_("Русский"), Languages.ru),
        (_("Английский"), Languages.en),
    ]
    return {
        "text": _("Выберете язык бота"),
        "languages": languages,
        "save": _("Сохранить"),
    }
