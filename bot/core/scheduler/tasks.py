from core.config import broker


async def remind_about_tasks_and_habits():
    await broker.publish(queue="remind_about_tasks")
    await broker.publish(queue="remind_about_habits")
