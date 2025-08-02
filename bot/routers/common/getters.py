from aiogram.utils.i18n import gettext as _


async def create_task_or_habit(**kwargs):
    return {
        "task_or_habit_text": _(
            "Вы хотите создать задачу или привычку?"
        ),
        "task_text": _("Задача"),
        "habit_text": _("Привычка"),
    }


async def view_tasks_or_habits(**kwargs):
    return {
        "tasks_or_habits_text": _(
            "Вы хотите узнать информацию о действующих задачах или привычках?"
        ),
        "tasks_text": _("Задачи"),
        "habits_text": _("Привычки"),
    }


async def edit_name(**kwargs):
    return {
        "item_name": _("Введите новое название"),
        "back": _("Отменить ввод названия"),
    }
