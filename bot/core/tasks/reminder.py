import asyncio
import datetime
import logging

from dependencies import HttpClient, Session

from core.config import app, bot, broker
from core.enums import Weekday
from core.utils.dt import get_moscow_dt
from routers.habits.repository import repository as habit_repository
from routers.tasks.repository import repository as task_repository

logger = logging.getLogger(__name__)


@broker.subscriber("remind_about_tasks")
async def reminder_about_tasks(client: HttpClient, session: Session):
    await task_repository.remind_about_items(
        client=client, session=session, bot=bot, params=None
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
    await habit_repository.remind_about_items(
        client=client,
        session=session,
        bot=bot,
        params={
            "day": day,
            "hour": hour,
        },
        date=str(utc_date),
        hour=hour,
    )


if __name__ == "__main__":
    asyncio.run(app.run())
