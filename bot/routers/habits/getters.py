from aiogram.utils.i18n import gettext as _


async def habit_name(**kwargs):
    return {
        "habit_name": _("Введите название привычки"),
        "back": _("Вернуться к выбору"),
    }


async def habit_purpose(**kwargs):
    return {
        "habit_purpose": _(
            "Введите, зачем вам эта привычка (для мотивации)"
        ),
        "back": _("Изменить название"),
    }
