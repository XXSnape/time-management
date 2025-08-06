from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager
from httpx import AsyncClient

from core.enums import Languages, Methods, Resources, Weekday
from core.keyboards.habits import completed_or_not_completed_habit_kb
from core.utils.quotes import add_motivation
from core.utils.request import make_request
from routers.common.repository import BaseRepository
from routers.habits.states import HabitsManagementStates


class HabitRepository(BaseRepository):
    resource = Resources.habits
    states = HabitsManagementStates

    @property
    def completed(self):
        return _("❤️Поздравляем с новой полезной привычкой!")

    @property
    def deleted(self):
        return _("✅Привычка успешно удалена!")

    @property
    def item_been_marked(self) -> str:
        return _("🙂Привычка уже отмечена!")

    async def make_request_to_mark_as_reminder(
        self,
        client: AsyncClient,
        callback: CallbackQuery,
        callback_data: CallbackData,
        access_token: str,
    ):
        await make_request(
            client=client,
            endpoint=f"habits/{callback_data.habit_id}/mark",
            method=Methods.post,
            access_token=access_token,
            json={
                "reminder_date": callback_data.date,
                "reminder_hour": callback_data.hour,
                "is_completed": callback_data.completed,
            },
            delete_markup=False,
        )
        if callback_data.completed:
            await callback.answer(
                _("✅Привычка отмечена как выполненная!"),
                show_alert=True,
            )
        else:
            await callback.answer(
                _("❌Привычка отмечена как невыполненная!"),
                show_alert=True,
            )

    def translate_reminder_item(
        self,
        item: dict,
        language: Languages,
        motivation: str | None,
    ) -> str:
        if language == Languages.ru:
            result = (
                "🔔Напоминание о привычке:\n\n"
                f"🏷️Название: {item['name']}"
            )
        else:
            result = (
                "🔔Reminder about the habit:\n\n"
                f"🏷️Title: {item['name']}"
            )
        return add_motivation(
            language=language, motivation=motivation, result=result
        )

    def generate_reminder_keyboard(
        self,
        language: Languages,
        item_id: int,
        **generate_kb_kwargs: int | str,
    ):
        return completed_or_not_completed_habit_kb(
            habit_id=item_id,
            language=language,
            **generate_kb_kwargs,
        )

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
            "🏷️Название: {name}\n\n"
            "✨Цель: {purpose}\n\n"
            "📅Дни напоминания: {days}\n\n"
            "⏰Часы напоминания: {hours}\n\n"
            "✅Количество успешных выполнений: {completed}\n\n"
            "🧮Всего отмечено напоминаний: {total}\n\n"
            "📊% Выполнений: {performance}\n\n"
            "🚩Успешно завершена - {is_completed}\n\n"
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
