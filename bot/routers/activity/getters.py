from aiogram.utils.i18n import gettext as _


async def change_activity(**kwargs):
    return {
        "text": _(
            "Если вы активируете бота, он будет присылать информацию о задачах и привычках, иначе не будет"
        ),
        "activate_text": _("Активировать"),
        "deactivate_text": _("Деактивировать"),
    }
