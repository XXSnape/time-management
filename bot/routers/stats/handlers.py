from typing import Literal

from aiogram.types import CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from httpx import AsyncClient

from backend.core.schemas.users import UserTelegramIdSchema
from core.enums import Methods
from core.utils.request import make_request
from database.dao.users import UsersDAO
import io
import csv
from aiogram.types import BufferedInputFile
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
    resource = dialog_manager.dialog_data["stats_type"]
    session = dialog_manager.middleware_data[
        "session_without_commit"
    ]
    user = await UsersDAO(session=session).find_one_or_none(
        UserTelegramIdSchema(
            telegram_id=dialog_manager.event.from_user.id
        )
    )
    client: AsyncClient = dialog_manager.middleware_data["client"]
    result = await make_request(
        client=client,
        endpoint=f"{resource}/statistics",
        method=Methods.get,
        access_token=user.access_token,
    )
    items = result["items"]
    times = [
        _("За последнюю неделю:"),
        _("За последний месяц:"),
        _("За последние 3 месяца:"),
        _("За последние 6 месяцев:"),
        _("За последние 9 месяцев:"),
        _("За последний год:"),
        _("За все время:"),
    ]
    text_result = ""
    if resource == "tasks":
        text_result += _(
            "📊Статистика по задачам за последнее время\n\n\n"
        )
        template = _(
            "📅{time}\n\n"
            "📌Всего задач: {total}\n"
            "✅Успешно выполнено: {completed}\n"
            "❌Не выполнено в срок: {not_completed}\n"
            "💯Результативность: {performance}%\n\n\n"
        )

        for time, item in zip(times, items):
            text_result += template.format(
                time=time,
                total=item["total"],
                completed=item["completed"],
                not_completed=item["not_completed"],
                performance=item["performance"],
            )

    else:
        text_result += _(
            "📊Статистика по количеству завершенных "
            "привычек за последнее время\n\n\n"
        )
        template = _("📅{time}\n📌Всего привычек: {total}\n\n\n")
        for time, item in zip(times, items):
            text_result += template.format(
                time=time,
                total=item["total"],
            )
    await dialog_manager.done()
    await callback.message.answer(text_result)


async def get_stats_by_file(
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
    result = await make_request(
        client=client,
        endpoint=f"{item}/statistics",
        method=Methods.get,
        access_token=user.access_token,
    )
    columns = [
        "period",
        "total",
    ]
    filename = "habits_statistics.csv"
    if item == "tasks":
        columns += [
            "completed",
            "not_completed",
            "performance (%)",
        ]
        filename = "tasks_statistics.csv"

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(columns)
    for stat in result["items"]:
        writer.writerow(list(stat.values()))
    csv_bytes = csv_buffer.getvalue().encode()
    csv_file = BufferedInputFile(file=csv_bytes, filename=filename)
    await dialog_manager.done()
    async with ChatActionSender.upload_document(
        chat_id=callback.from_user.id, bot=callback.bot
    ):
        await callback.message.answer_document(document=csv_file)
