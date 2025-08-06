from core.config import scheduler

from .tasks import remind_about_tasks_and_habits


def register_tasks():
    scheduler.add_job(
        remind_about_tasks_and_habits,
        "cron",
        hour="0-23",
        minute="0",
        second="0",
        id="remind_about_tasks_and_habits",
        replace_existing=True,
    )
