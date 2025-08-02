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


async def delete_habit(**kwargs):
    return {
        "confirm_text": _(
            "Вы точно хотите удалить эту привычку? Отменить это действие будет нельзя."
        ),
        "confirm_delete_habit_text": _("Удалить привычку"),
        "back": _("Вернуться к деталям"),
    }


async def edit_habit(
    dialog_manager: DialogManager,
    **kwargs,
):
    habit_id = dialog_manager.dialog_data["current_item"]
    habit_data = dialog_manager.dialog_data[f"item_{habit_id}_data"]
    habit_text = habit_data["text"]
    return {
        "habit_text": habit_text,
        "name_text": _("Название"),
        "purpose_text": _("Цель"),
        "days_text": _("Дни напоминаний"),
        "hours_text": _("Часы напоминаний"),
        "mark_text": _("Отметить завершённой"),
        "back": _("Вернуться к деталям"),
    }


async def edit_habit_purpose(**kwargs):
    return {
        "habit_purpose": _("Введите новую цель для привычки"),
        "back": _("Отменить ввод цели"),
    }


def get_texts_by_habits(habits: list[dict]):
    texts = []
    for habit in habits:
        current_text = _("{name}").format(
            name=habit["name"],
        )
        texts.append([current_text, habit["id"]])
    return texts
