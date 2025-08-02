from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram.utils.i18n import gettext as _

from httpx import AsyncClient

from core.enums import Methods, Weekday
from core.schemas.users import UserTelegramIdSchema
from core.utils.dt import get_pretty_date
from core.utils.request import make_request
from database.dao.users import UsersDAO
from .states import CreateHabitStates, HabitsManagementStates


async def start_create_habit(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        CreateHabitStates.name,
        mode=StartMode.RESET_STACK,
    )


async def start_view_habits(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        HabitsManagementStates.view_all,
        mode=StartMode.RESET_STACK,
    )


async def save_checkbox(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    checkbox = dialog_manager.find("multi_days").get_checked()
    dialog_manager.dialog_data.update(days=checkbox)
    await dialog_manager.next()


async def save_habit(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    checkbox = dialog_manager.find("multi_hours").get_checked()
    client: AsyncClient = dialog_manager.middleware_data["client"]
    session = dialog_manager.middleware_data[
        "session_without_commit"
    ]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(telegram_id=callback.from_user.id)
    )
    await make_request(
        client=client,
        endpoint="habits",
        method=Methods.post,
        access_token=user.access_token,
        json={
            "name": dialog_manager.dialog_data["name"],
            "purpose": dialog_manager.dialog_data["purpose"],
            "days": dialog_manager.dialog_data["days"],
            "hours": checkbox,
        },
    )
    await callback.answer(
        _("Привычка успешно создана!"), show_alert=True
    )
    await dialog_manager.done()


def generate_habit_info(
    dialog_manager: DialogManager,
    item: dict,
    item_id: str | int,
):
    is_completed = "✅" if item["date_of_completion"] else "❌"
    translates = {
        Weekday.monday: _("Понедельник"),
        Weekday.tuesday: _("Вторник"),
        Weekday.wednesday: _("Среда"),
        Weekday.thursday: _("Четверг"),
        Weekday.friday: _("Пятница"),
        Weekday.saturday: _("Суббота"),
        Weekday.sunday: _("Воскресенье"),
    }
    text = _(
        "Название: {name}\n\n"
        "Цель: {purpose}\n\n"
        "Дни напоминания: {days}\n\n"
        "Часы напоминания: {hours}\n\n"
        "Количество успешных выполнений: {completed}\n\n"
        "Всего было напоминаний: {total}\n\n"
        "% Выполнений: {performance}\n\n"
        "Создана: {created}\n\n"
        "Успешно завершена - {is_completed}\n\n"
    ).format(
        name=item["name"],
        purpose=item["purpose"],
        days=", ".join(translates[d] for d in item["days"]),
        hours=", ".join(str(h) for h in item["hours"]),
        completed=item["completed"],
        total=item["total"],
        performance=item["performance"],
        created=get_pretty_date(item["created"]),
        is_completed=is_completed,
    )
    dialog_manager.dialog_data.update(
        {
            f"item_{item_id}_data": {
                "text": text,
                "days": item["days"],
                "hours": item["hours"],
            },
            "current_item": int(item_id),
        }
    )
