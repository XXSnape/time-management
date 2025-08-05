import datetime

import pytest
from httpx import AsyncClient, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def test_get_active_user_tasks(ac: AsyncClient):
    response = await ac.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert [1, 2, 3] == [task["id"] for task in data["items"]]
    assert data["pages"] == 1
    assert data["total_count"] == 3


@pytest.mark.parametrize(
    "ids, params",
    [
        ([1, 2], {"page": 1, "per_page": 2}),
        ([3], {"page": 2, "per_page": 2}),
    ],
)
async def test_pagination(
    ac: AsyncClient,
    ids: list[int],
    params: dict[str, int],
):
    response = await ac.get("/tasks", params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == params["page"]
    assert data["pages"] == 2
    assert ids == [task["id"] for task in data["items"]]


async def test_get_all_tasks_by_hour(ac: AsyncClient):
    response = await ac.get("/tasks/schedules")
    assert response.status_code == 200
    data = response.json()
    assert [1, 2] == [task["id"] for task in data["items"]]


@pytest.mark.parametrize(
    "name, description, deadline_delta, hour_before_reminder",
    [
        ("Новая задача", "Описание", 1, 2),
        ("ОченьДлинноеИмя" * 10, "Слишком длинное имя", 1, 2),
    ],
)
async def test_create_task(
    ac: AsyncClient,
    async_session: AsyncSession,
    name: str,
    description: str,
    deadline_delta: int,
    hour_before_reminder: int,
):
    deadline = (
        datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(days=deadline_delta)
    ).isoformat()
    response = await ac.post(
        "/tasks",
        json={
            "name": name,
            "description": description,
            "deadline_datetime": deadline,
            "hour_before_reminder": hour_before_reminder,
        },
    )
    if len(name) > 50:
        assert response.status_code == 422
    else:
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name
        assert data["description"] == description


async def test_create_task_past_deadline(ac: AsyncClient):
    past_deadline = (datetime.datetime.now(datetime.UTC)).isoformat()
    response = await ac.post(
        "/tasks",
        json={
            "name": "Просроченная",
            "description": "Дедлайн в прошлом",
            "deadline_datetime": past_deadline,
            "hour_before_reminder": 2,
        },
    )
    assert response.status_code == 409


async def test_get_task_by_id(ac: AsyncClient):
    response = await ac.get("tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Task 1"
    assert data["description"] == "Первое задание"
    assert data["hour_before_reminder"] == 2
    assert data["id"] == 1


async def test_update_task(ac: AsyncClient):
    new_name = "Обновлено"
    response = await ac.patch(
        "tasks/1",
        json={"name": new_name},
    )
    assert response.status_code == 200
    assert response.json()["name"] == new_name


async def test_update_task_invalid_deadline(ac: AsyncClient):
    past_deadline = (datetime.datetime.now(datetime.UTC)).isoformat()
    response = await ac.patch(
        "tasks/1",
        json={"deadline_datetime": past_deadline},
    )
    assert response.status_code == 409


async def test_update_task_not_found(ac: AsyncClient):
    response = await ac.patch(
        "/99999",
        json={"name": "Не найдено"},
    )
    assert response.status_code == 404


async def test_mark_task_completed(ac: AsyncClient):
    today = datetime.datetime.now(datetime.UTC).date().isoformat()
    response = await ac.patch(
        "tasks/1/completion",
        json={"date_of_completion": today},
    )
    assert response.status_code == 200
    assert "pages" in response.json()
    response2 = await ac.get("/tasks/1")
    assert response2.status_code == 200
    data = response2.json()
    assert data["date_of_completion"] == today


async def test_mark_task_already_completed(ac: AsyncClient):
    today = datetime.datetime.now(datetime.UTC).date().isoformat()
    response = await ac.patch(
        "tasks/4/completion",
        json={"date_of_completion": today},
    )
    assert response.status_code == 404


async def test_delete_task(ac: AsyncClient, user2_token: str):
    request = Request(
        "DELETE",
        "http://test/api/v1/tasks/2",
        cookies={"access-token": user2_token},
    )
    response = await ac.send(request)
    assert response.status_code == 404
    response = await ac.delete("/tasks/2")
    assert response.status_code == 200
    response2 = await ac.get("/tasks/2")
    assert response2.status_code == 404
