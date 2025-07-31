from aiogram.utils.i18n import gettext as _


async def create_task_or_habit(**kwargs):
    return {
        "task_or_habit_text": _(
            "Вы хотите создать задачу или привычку?"
        ),
        "task_text": _("Задача"),
        "habit_text": _("Привычка"),
    }
