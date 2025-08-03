import asyncio

from core.config import broker, app, bot
from core.keyboards.tasks import complete_task_kb
from core.utils.dt import get_pretty_dt
from database.dao.users import UsersDAO
from dependencies import HttpClient, Session
from core.enums import Methods, Languages
from core.utils.request import make_request


def translate_task(language: Languages, name: str, deadline: str):
    moscow_dt = get_pretty_dt(deadline)
    if language == Languages.ru:
        return (
            "Напоминание о задаче:\n\n"
            f"Название: {name}\n\n"
            f"Дата и время дедлайна: {moscow_dt}",
            "Отметить выполненной",
        )
    return (
        "Reminder about the task:\n\n"
        f"Title: {name}\n\n"
        f"Deadline date and time: {moscow_dt}",
        "Mark Completed",
    )


@broker.subscriber("remind_about_tasks")
async def reminder(client: HttpClient, session: Session):
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
        text, btn_text = translate_task(
            language=language,
            name=task["name"],
            deadline=task["deadline_datetime"],
        )
        await bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=complete_task_kb(
                task_id=task["id"], text=btn_text
            ),
        )


if __name__ == "__main__":
    asyncio.run(app.run())
