import datetime

from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager

from core.utils.dt import get_pretty_dt, get_moscow_dt
from core.utils.generator import generate_hours


async def task_name(**kwargs):
    return {
        "task_name": _("🏷️Введите название задачи"),
        "back": _("⬅️Вернуться к выбору"),
    }


async def task_description(**kwargs):
    return {
        "task_description": _("✨Введите описание задачи"),
        "back": _("⬅️Вернуться к названию"),
    }


async def edit_task_description(**kwargs):
    return {
        "task_description": _("✨Введите новое описание для задачи"),
        "back": _("⬅️Отменить ввод описания"),
    }


async def task_date(**kwargs):
    return {
        "calendar": _("📅Выберите дату дедлайна"),
        "back": _("⬅️Изменить описание"),
    }


async def task_hour(dialog_manager: DialogManager, **kwargs):
    moscow_dt = get_moscow_dt()
    hour = 0
    if (
        datetime.datetime.strptime(
            dialog_manager.dialog_data["date"], "%Y-%m-%d"
        ).date()
        == moscow_dt.date()
    ):
        hour = (moscow_dt.hour + 1) % 24
    return {
        "hours": generate_hours(start_hour=hour, end_hour=24),
        "hour_text": _("⏰Выберете час дедлайна"),
        "back": _("⬅️Изменить дату дедлайна"),
    }


async def task_notification_hour(**kwargs):
    return {
        "hours": generate_hours(start_hour=1, end_hour=25),
        "notification_hour_text": _(
            "🕒Выберете, за сколько часов до дедлайна нужно напомнить о задаче"
        ),
        "back": _("⬅️Изменить час дедлайна"),
    }


async def edit_task_notification_hour(**kwargs):
    return {
        "hours": generate_hours(start_hour=1, end_hour=25),
        "notification_hour_text": _(
            "🕒Измените, за сколько часов до дедлайна нужно напомнить о задаче"
        ),
        "back": _("⬅️Отменить редактирование часов до напоминания"),
    }


async def change_deadline_date(**kwargs):
    return {
        "calendar": _("📅Выберете новую дату дедлайна"),
        "back": _("⬅️Отменить выбор даты"),
    }


def get_texts_by_tasks(tasks: list[dict]):
    texts = []
    for task in tasks:
        current_text = _("{name} [{deadline}]").format(
            name=task["name"],
            deadline=get_pretty_dt(task["deadline_datetime"]),
        )
        texts.append([current_text, task["id"]])
    return texts


async def delete_task(
    **kwargs,
):
    return {
        "confirm_text": _(
            "🤔Вы точно хотите удалить эту задачу? Отменить это действие будет нельзя."
        ),
        "confirm_delete_task_text": _("🗑️Удалить задачу"),
        "back": _("⬅️Вернуться к деталям"),
    }


async def edit_task(
    dialog_manager: DialogManager,
    **kwargs,
):
    task_id = dialog_manager.dialog_data["current_item"]
    task_data = dialog_manager.dialog_data[f"item_{task_id}_data"]
    task_text = task_data["text"]
    return {
        "task_text": task_text,
        "name": _("🏷️Название"),
        "description_text": _("✨Описание"),
        "deadline_date_text": _("📆Дата дедлайна"),
        "deadline_time_text": _("⏰Время дедлайна"),
        "notification_hour_text": _(
            "🕒Количество часов до напоминания"
        ),
        "mark_text": _("✅Отметить выполненной"),
        "back": _("⬅️Вернуться к деталям"),
    }


async def change_deadline_time(**kwargs):
    return {
        "hours": generate_hours(start_hour=0, end_hour=24),
        "hour_text": _("⏰Выберете новый час дедлайна"),
        "back": _("⬅️Отменить выбор часа дедлайна"),
    }
