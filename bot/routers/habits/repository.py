from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager

from core.enums import Resources, Weekday
from core.utils.dt import get_pretty_date
from routers.common.base import BaseRepository
from routers.habits.states import HabitsManagementStates


class HabitRepository(BaseRepository):
    resource = Resources.habits
    states = HabitsManagementStates

    @property
    def completed(self):
        return _("Поздравляем с новой полезной привычкой!")

    @property
    def deleted(self):
        return _("Привычка успешно удалена!")

    def get_texts_by_items(
        self, items: list[dict]
    ) -> list[list[str | int]]:
        texts = []
        for habit in items:
            current_text = _("{name}").format(
                name=habit["name"],
            )
            texts.append([current_text, habit["id"]])
        return texts

    def generate_item_info(
        self,
        dialog_manager: DialogManager,
        item: dict,
        item_id: str | int,
    ) -> None:
        is_completed = "✅" if item["date_of_completion"] else "❌"
        weekdays = list(Weekday)
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
            days=", ".join(
                translates[d]
                for d in sorted(
                    item["days"], key=lambda d: weekdays.index(d)
                )
            ),
            hours=", ".join(
                str(h)
                for h in sorted(item["hours"], key=lambda h: int(h))
            ),
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


repository = HabitRepository()
