from aiogram.utils.i18n import gettext as _


async def stats_tasks_or_habits(**kwargs):
    return {
        "tasks_or_habits_text": _(
            "Нужна статистика о задачах или привычках?"
        ),
        "habits_text": _("Привычки"),
        "tasks_text": _("Задачи"),
    }


async def text_or_file(**kwargs):
    return {
        "text_or_file": _(
            "Нужна статистика текстом или csv файлом?"
        ),
        "text": _("Текст"),
        "file": _("Файл"),
        "back": _("Назад к выбору"),
    }
