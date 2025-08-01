from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager

from core.enums import Weekday
from core.utils.generator import generate_hours


async def habit_name(**kwargs):
    return {
        "habit_name": _("Введите название привычки"),
        "back": _("Вернуться к выбору"),
    }


async def habit_purpose(**kwargs):
    return {
        "habit_purpose": _(
            _("Введите, зачем вам эта привычка (для мотивации)")
        ),
        "back": _("Изменить название"),
    }


async def get_days_of_week(dialog_manager: DialogManager, **kwargs):
    checkbox = dialog_manager.find("multi_days").get_checked()
    return {
        "days_text": _(
            _("Выберете дни недели, когда вам присылать напоминание")
        ),
        "days": [
            (_("Понедельник"), Weekday.monday),
            (_("Вторник"), Weekday.tuesday),
            (_("Среда"), Weekday.wednesday),
            (_("Четверг"), Weekday.thursday),
            (_("Пятница"), Weekday.friday),
            (_("Суббота"), Weekday.saturday),
            (_("Воскресенье"), Weekday.sunday),
        ],
        "save_text": _("Сохранить"),
        "back": _("Изменить цель привычки"),
        "can_be_saved": bool(checkbox),
    }


async def get_hours(dialog_manager: DialogManager, **kwargs):
    checkbox = dialog_manager.find("multi_hours").get_checked()
    return {
        "hours_text": _(
            _("Выберете часы, когда вам отправлять напоминание")
        ),
        "hours": generate_hours(start_hour=0, end_hour=24),
        "save_text": _("Сохранить"),
        "back": _("Изменить дни недели"),
        "can_be_saved": bool(checkbox),
    }
