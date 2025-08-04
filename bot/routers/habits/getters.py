from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager

from core.enums import Weekday
from core.utils.generator import generate_hours


async def habit_name(**kwargs):
    return {
        "habit_name": _("🏷️Введите название привычки"),
        "back": _("⬅️Вернуться к выбору"),
    }


async def habit_purpose(**kwargs):
    return {
        "habit_purpose": _(
            _("✨Введите, зачем вам эта привычка (для мотивации)")
        ),
        "back": _("⬅️Изменить название"),
    }


def get_days():
    return [
        (_("Понедельник"), Weekday.monday),
        (_("Вторник"), Weekday.tuesday),
        (_("Среда"), Weekday.wednesday),
        (_("Четверг"), Weekday.thursday),
        (_("Пятница"), Weekday.friday),
        (_("Суббота"), Weekday.saturday),
        (_("Воскресенье"), Weekday.sunday),
    ]


async def get_days_of_week(dialog_manager: DialogManager, **kwargs):
    checkbox = dialog_manager.find("multi_days").get_checked()
    return {
        "days_text": _(
            _(
                "📅Выберете дни недели, когда вам присылать напоминание"
            )
        ),
        "days": get_days(),
        "save_text": _("💾Сохранить"),
        "back": _("⬅️Изменить цель привычки"),
        "can_be_saved": bool(checkbox),
    }


async def get_hours(dialog_manager: DialogManager, **kwargs):
    checkbox = dialog_manager.find("multi_hours").get_checked()
    return {
        "hours_text": _(
            _("⏰Выберете часы, когда вам отправлять напоминание")
        ),
        "hours": generate_hours(start_hour=0, end_hour=24),
        "save_text": _("💾Сохранить"),
        "back": _("⬅️Изменить дни недели"),
        "can_be_saved": bool(checkbox),
    }


async def delete_habit(**kwargs):
    return {
        "confirm_text": _(
            "🤔Вы точно хотите удалить эту привычку? Отменить это действие будет нельзя."
        ),
        "confirm_delete_habit_text": _("🗑️Удалить привычку"),
        "back": _("⬅️Вернуться к деталям"),
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
        "name_text": _("🏷️Название"),
        "purpose_text": _("✨Цель"),
        "days_text": _("📅Дни напоминаний"),
        "hours_text": _("⏰Часы напоминаний"),
        "mark_text": _("✅Отметить завершённой"),
        "back": _("⬅️Вернуться к деталям"),
    }


async def edit_habit_purpose(**kwargs):
    return {
        "habit_purpose": _("✨Введите новую цель для привычки"),
        "back": _("⬅️Отменить ввод цели"),
    }


async def edit_by_multiselect(
    dialog_manager: DialogManager,
    data: list[list[str] | tuple[str, str]],
    key: str,
    multiselect_id: str,
):
    habit_id = dialog_manager.dialog_data["current_item"]
    habit_data = dialog_manager.dialog_data[f"item_{habit_id}_data"]
    selected = [str(item) for item in habit_data[key]]
    multiselect = dialog_manager.find(multiselect_id)
    first = dialog_manager.dialog_data.get("is_first_viewing")
    if first is None:
        for __, item_id in data:
            if item_id in selected:
                await multiselect.set_checked(item_id, True)
        dialog_manager.dialog_data["is_first_viewing"] = False


async def edit_habit_days(
    dialog_manager: DialogManager,
    **kwargs,
):
    days = get_days()
    await edit_by_multiselect(
        dialog_manager=dialog_manager,
        data=days,
        key="days",
        multiselect_id="multi_days",
    )
    return {
        "habit_days": _(
            "📅Выберете дни, когда вам присылать напоминание о привычке"
        ),
        "days": days,
        "back": _("⬅️Отменить выбор дней"),
        "save_text": _("💾Сохранить"),
    }


async def edit_habit_hours(dialog_manager: DialogManager, **kwargs):
    hours = generate_hours(start_hour=0, end_hour=24)
    await edit_by_multiselect(
        dialog_manager=dialog_manager,
        data=hours,
        key="hours",
        multiselect_id="multi_hours",
    )
    return {
        "habit_hours": _(
            "⏰Выберете часы, когда вам отправлять напоминания"
        ),
        "hours": hours,
        "back": _("⬅️Отменить выбор часов"),
        "save_text": _("💾Сохранить"),
    }


def get_texts_by_habits(habits: list[dict]):
    texts = []
    for habit in habits:
        current_text = _("{name}").format(
            name=habit["name"],
        )
        texts.append([current_text, habit["id"]])
    return texts
