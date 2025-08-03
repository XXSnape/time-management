import asyncio
import datetime

from core.config import broker, app, bot
from core.keyboards.habits import completed_or_not_completed_habit_kb
from core.keyboards.tasks import complete_task_kb
from core.utils.dt import get_pretty_dt, get_moscow_dt
from database.dao.users import UsersDAO
from dependencies import HttpClient, Session
from core.enums import Methods, Languages, Weekday
from core.utils.request import make_request


def translate_task(
    language: Languages, name: str, deadline: str
) -> str:
    moscow_dt = get_pretty_dt(deadline)
    if language == Languages.ru:
        return (
            "Напоминание о задаче:\n\n"
            f"Название: {name}\n\n"
            f"Дата и время дедлайна: {moscow_dt}"
        )
    return (
        "Reminder about the task:\n\n"
        f"Title: {name}\n\n"
        f"Deadline date and time: {moscow_dt}"
    )


def translate_habit(language: Languages, name: str) -> str:
    if language == Languages.ru:
        return "Напоминание о привычке:\n\n" f"Название: {name}\n\n"
    return "Reminder about the habit:\n\n" f"Title: {name}\n\n"


@broker.subscriber("remind_about_tasks")
async def reminder_about_tasks(client: HttpClient, session: Session):
    tasks = await make_request(
        client=client,
        endpoint="tasks/schedules",
        method=Methods.get,
    )
    users = set(
        task["user"]["telegram_id"] for task in tasks["items"]
    )
    user_with_locale = await UsersDAO(
        session=session
    ).get_user_locales(users)
    user_and_locale = {
        telegram_id: telegram_id
        for telegram_id, locale in user_with_locale
    }
    for task in tasks["items"]:
        user_id = task["user"]["telegram_id"]
        language = user_and_locale.get(user_id, Languages.ru)
        text = translate_task(
            language=language,
            name=task["name"],
            deadline=task["deadline_datetime"],
        )
        await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=complete_task_kb(
                language=language,
                task_id=task["id"],
            ),
        )


@broker.subscriber("remind_about_habits")
async def reminder_about_habits(
    client: HttpClient, session: Session
):
    moscow_dt = get_moscow_dt()
    utc_date = datetime.datetime.now(datetime.UTC).date()
    weekdays = {num: day for num, day in zip(range(7), Weekday)}
    day = weekdays[moscow_dt.date().weekday()]
    hour = moscow_dt.hour
    habits = await make_request(
        client=client,
        endpoint="habits/schedules",
        method=Methods.get,
        params={
            "day": day,
            "hour": hour,
        },
    )
    users = set(
        task["user"]["telegram_id"] for task in habits["items"]
    )
    user_with_locale = await UsersDAO(
        session=session
    ).get_user_locales(users)
    user_and_locale = {
        telegram_id: telegram_id
        for telegram_id, locale in user_with_locale
    }
    for habit in habits["items"]:
        user_id = habit["user"]["telegram_id"]
        language = user_and_locale.get(user_id, Languages.ru)
        text = translate_habit(language=language, name=habit["name"])
        await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=completed_or_not_completed_habit_kb(
                habit_id=habit["id"],
                language=language,
                date=str(utc_date),
                hour=hour,
            ),
        )


if __name__ == "__main__":
    asyncio.run(app.run())
