from datetime import date

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from core.enums import Resources
from core.exc import ServerIsUnavailableExc
from core.utils.dt import (
    get_pretty_dt,
    parse_utc_string_to_dt,
    convert_utc_to_moscow,
    convert_moscow_dt_to_utc,
    selected_date_validator,
)
from routers.common.base import BaseRepository
from routers.tasks.handlers import catching_deadline_error
from routers.tasks.states import TasksManagementStates
from aiogram.utils.i18n import gettext as _


class TaskRepository(BaseRepository):
    resource = Resources.tasks
    states = TasksManagementStates

    @property
    def completed(self):
        return _("Задача успешно выполнена! Поздравляем!")

    @property
    def deleted(self):
        return _("Задача успешно удалена!")

    def get_texts_by_items(
        self, items: list[dict]
    ) -> list[list[str | int]]:
        texts = []
        for task in items:
            current_text = _("{name} [{deadline}]").format(
                name=task["name"],
                deadline=get_pretty_dt(task["deadline_datetime"]),
            )
            texts.append([current_text, task["id"]])
        return texts

    def generate_item_info(
        self,
        dialog_manager: DialogManager,
        item: dict,
        item_id: str | int,
    ) -> None:
        completed = "✅" if item["date_of_completion"] else "❌"
        text = _(
            "Название: {name}\n\n"
            "Описание: {description}\n\n"
            "Количество часов до напоминания о дедлайне: {hours}\n\n"
            "Дата дедлайна: {deadline}\n\n"
            "Успешно завершена - {completed}"
        ).format(
            name=item["name"],
            description=item["description"],
            hours=item["hour_before_reminder"],
            deadline=get_pretty_dt(item["deadline_datetime"]),
            completed=completed,
        )
        dialog_manager.dialog_data.update(
            {
                f"item_{item_id}_data": {
                    "text": text,
                    "deadline_utc": item["deadline_datetime"],
                },
                "current_item": int(item_id),
            }
        )

    async def change_notification_hour(
        self,
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str,
    ):

        await self._change_item_and_go_next(
            dialog_manager=dialog_manager,
            item="hour_before_reminder",
            value=int(item_id),
        )

    async def _change_deadline(
        self,
        manager: DialogManager,
        callback: CallbackQuery,
        **kwargs: int,
    ):

        task_id = manager.dialog_data["current_task"]
        deadline_utc = manager.dialog_data[f"task_{task_id}_data"][
            "deadline_utc"
        ]
        utc_dt = parse_utc_string_to_dt(deadline_utc)
        moscow_dt = convert_utc_to_moscow(utc_dt)
        moscow_dt = moscow_dt.replace(**kwargs)
        new_utc_dt = convert_moscow_dt_to_utc(moscow_dt=moscow_dt)
        try:
            await self._change_item_and_go_next(
                dialog_manager=manager,
                item="deadline_datetime",
                value=str(new_utc_dt),
            )
        except ServerIsUnavailableExc as e:
            await catching_deadline_error(
                callback=callback, e=e, create=False
            )

    async def change_deadline_date(
        self,
        callback: CallbackQuery,
        widget,
        manager: DialogManager,
        selected_date: date,
    ):
        res = await selected_date_validator(
            callback=callback, selected_date=selected_date
        )
        if not res:
            return
        await self._change_deadline(
            manager=manager,
            callback=callback,
            year=selected_date.year,
            month=selected_date.month,
            day=selected_date.day,
        )

    async def change_deadline_time(
        self,
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str,
    ):
        await self._change_deadline(
            manager=dialog_manager,
            callback=callback,
            hour=int(item_id),
        )


repository = TaskRepository()
