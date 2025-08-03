from typing import Literal

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from httpx import AsyncClient

from backend.core.schemas.users import UserTelegramIdSchema
from core.enums import Methods
from core.utils.request import make_request
from database.dao.users import UsersDAO
from aiogram.utils.i18n import gettext as _


def choosing_statistics(stats_type: Literal["tasks", "habits"]):
    async def _wrapper(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ):
        dialog_manager.dialog_data["stats_type"] = stats_type
        await dialog_manager.next()

    return _wrapper


async def get_stats_by_text(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    item = dialog_manager.dialog_data["stats_type"]
    session = dialog_manager.middleware_data[
        "session_without_commit"
    ]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(
            telegram_id=dialog_manager.event.from_user.id
        )
    )
    client: AsyncClient = dialog_manager.middleware_data["client"]
    await dialog_manager.done()
    if item == "tasks":
        result = await make_request(
            client=client,
            endpoint="tasks/statistics",
            method=Methods.get,
            access_token=user.access_token,
        )
        items = result["items"]
        text_result = _(
            "Статистика за последнее время\n\n\n"
            "За последнюю неделю:\n\n"
            "Всего задач: {week_1_total}\n"
            "Успешно выполнено: {week_1_completed}\n"
            "Не выполнено в срок: {week_1_not_completed}\n"
            "Результативность: {week_1_performance}%\n\n\n"
            #
            "За последний месяц:\n\n"
            "Всего задач: {month_1_total}\n"
            "Успешно выполнено: {month_1_completed}\n"
            "Не выполнено в срок: {month_1_not_completed}\n"
            "Результативность: {month_1_performance}%\n\n\n"
            #
            "За последние 3 месяца:\n\n"
            "Всего задач: {month_3_total}\n"
            "Успешно выполнено: {month_3_completed}\n"
            "Не выполнено в срок: {month_3_not_completed}\n"
            "Результативность: {month_3_performance}%\n\n\n"
            #
            "За последние 6 месяцев:\n\n"
            "Всего задач: {month_6_total}\n"
            "Успешно выполнено: {month_6_completed}\n"
            "Не выполнено в срок: {month_6_not_completed}\n"
            "Результативность: {month_6_performance}%\n\n\n"
            #
            "За последние 9 месяцев:\n\n"
            "Всего задач: {month_9_total}\n"
            "Успешно выполнено: {month_9_completed}\n"
            "Не выполнено в срок: {month_9_not_completed}\n"
            "Результативность: {month_9_performance}%\n\n\n"
            #
            "За последний год:\n\n"
            "Всего задач: {year_1_total}\n"
            "Успешно выполнено: {year_1_completed}\n"
            "Не выполнено в срок: {year_1_not_completed}\n"
            "Результативность: {year_1_performance}%\n\n\n"
            #
            "За все время:\n\n"
            "Всего задач: {all_total}\n"
            "Успешно выполнено: {all_completed}\n"
            "Не выполнено в срок: {all_not_completed}\n"
            "Результативность: {all_performance}%"
        ).format(
            week_1_total=items[0]["total"],
            week_1_completed=items[0]["completed"],
            week_1_not_completed=items[0]["not_completed"],
            week_1_performance=items[0]["performance"],
            month_1_total=items[1]["total"],
            month_1_completed=items[1]["completed"],
            month_1_not_completed=items[1]["not_completed"],
            month_1_performance=items[1]["performance"],
            month_3_total=items[2]["total"],
            month_3_completed=items[2]["completed"],
            month_3_not_completed=items[2]["not_completed"],
            month_3_performance=items[2]["performance"],
            month_6_total=items[3]["total"],
            month_6_completed=items[3]["completed"],
            month_6_not_completed=items[3]["not_completed"],
            month_6_performance=items[3]["performance"],
            month_9_total=items[4]["total"],
            month_9_completed=items[4]["completed"],
            month_9_not_completed=items[4]["not_completed"],
            month_9_performance=items[4]["performance"],
            year_1_total=items[5]["total"],
            year_1_completed=items[5]["completed"],
            year_1_not_completed=items[5]["not_completed"],
            year_1_performance=items[5]["performance"],
            all_total=items[6]["total"],
            all_completed=items[6]["completed"],
            all_not_completed=items[6]["not_completed"],
            all_performance=items[6]["performance"],
        )
        await callback.message.answer(text_result)
