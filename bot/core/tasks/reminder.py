import asyncio
import datetime
import logging

from core.config import broker, app, bot
from core.keyboards.habits import completed_or_not_completed_habit_kb
from core.keyboards.tasks import complete_task_kb
from core.tasks.utils import (
    get_ru_and_en_quotes,
    translate_task,
    translate_habit,
    get_users_locales,
)
from core.utils.dt import get_moscow_dt
from dependencies import HttpClient, Session
from core.enums import Methods, Languages, Weekday
from core.utils.request import make_request


logger = logging.getLogger(__name__)


@broker.subscriber("remind_about_tasks")
async def reminder_about_tasks(client: HttpClient, session: Session):
    quotes = await get_ru_and_en_quotes(client)

    tasks = await make_request(
        client=client,
        endpoint="tasks/schedules",
        method=Methods.get,
    )
    user_and_locale = await get_users_locales(
        items=tasks["items"], session=session
    )
    for task in tasks["items"]:
        user_id = task["user"]["telegram_id"]
        language = user_and_locale.get(user_id, Languages.ru)
        text = translate_task(
            language=language,
            name=task["name"],
            deadline=task["deadline_datetime"],
            motivation=quotes[language],
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
    quotes = await get_ru_and_en_quotes(client)
    habits = await make_request(
        client=client,
        endpoint="habits/schedules",
        method=Methods.get,
        params={
            "day": day,
            "hour": hour,
        },
    )
    user_and_locale = await get_users_locales(
        items=habits["items"], session=session
    )
    for habit in habits["items"]:
        user_id = habit["user"]["telegram_id"]
        language = user_and_locale.get(user_id, Languages.ru)
        text = translate_habit(
            language=language,
            name=habit["name"],
            motivation=quotes[language],
        )
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
