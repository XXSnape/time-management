from core.config import scheduler
from .tasks import remind_about_tasks_and_habits


def register_tasks():
    scheduler.add_job(
        remind_about_tasks_and_habits,
        "cron",
        hour="0-23",
        minute="0-59",
        second="1",
    )
