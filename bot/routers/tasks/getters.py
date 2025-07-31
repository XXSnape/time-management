from aiogram.utils.i18n import gettext as _


async def task_name(**kwargs):
    return {
        "task_name": _("Введите название привычки"),
        "back": _("Вернуться к выбору"),
        "cancel": _("Отменить"),
    }

async def task_date(**kwargs):
    return {
        "calendar": _("Выберите дату дедлайна"),
        "back": _("Изменить название"),
        "cancel": _("Отменить"),
    }
