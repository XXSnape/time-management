import datetime

from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager


def generate_hours(start_hour: int):
    return [(str(h).zfill(2), h) for h in range(start_hour, 24)]


async def task_name(**kwargs):
    return {
        "task_name": _("Введите название задачи"),
        "back": _("Вернуться к выбору"),
    }


async def task_description(**kwargs):
    return {
        "task_description": _("Введите описание задачи"),
        "back": _("Вернуться к названию"),
    }


async def task_date(**kwargs):
    return {
        "calendar": _("Выберите дату дедлайна"),
        "back": _("Изменить описание"),
    }


async def task_hour(dialog_manager: DialogManager, **kwargs):
    moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
    moscow_dt = datetime.datetime.now(moscow_tz)
    hour = 0
    if (
        datetime.datetime.strptime(
            dialog_manager.dialog_data["date"], "%Y-%m-%d"
        ).date()
        == moscow_dt.date()
    ):
        hour = (moscow_dt.hour + 1) % 24
    return {
        "hours": generate_hours(start_hour=hour),
        "hour_text": _("Выберете час дедлайна"),
        "back": _("Изменить дату дедлайна"),
    }


async def task_notification_hour(**kwargs):
    return {
        "hours": generate_hours(start_hour=0),
        "notification_hour_text": _(
            "Выберете, за сколько часов до дедлайна нужно напомнить о задаче"
        ),
        "back": _("Изменить час дедлайна"),
    }
