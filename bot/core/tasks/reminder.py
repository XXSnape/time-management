import asyncio

from core.enums import Weekday
from core.config import broker, app
from dependencies import HttpClient
from core.enums import Methods
from core.utils.request import make_request


@broker.subscriber("reminder")
async def reminder(client: HttpClient):
    tasks = await make_request(
        client=client,
        endpoint="habits/schedules",
        method=Methods.get,
        params={
            "day": Weekday.friday,
            "hour": 7,
        },
    )
    print("tasks", tasks)


if __name__ == "__main__":
    asyncio.run(app.run())
