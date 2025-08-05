import pytest
from core.utils.enums import Weekday


@pytest.mark.parametrize(
    "day,hour,expected_count",
    [
        (Weekday.MONDAY, 7, 1),  # habit1, timer 7, monday
        (
            Weekday.TUESDAY,
            8,
            2,
        ),  # habit1 (timer 8, tuesday), habit2 (timer 8, tuesday)
        (Weekday.WEDNESDAY, 21, 1),  # habit2, timer 21, wednesday
        (Weekday.SUNDAY, 8, 0),  # habit3, timer 8, sunday завершена
        (Weekday.FRIDAY, 7, 0),  # нет привычек на пятницу
    ],
)
async def test_get_habits_on_schedule(ac, day, hour, expected_count):
    response = await ac.get(
        "/habits/schedules", params={"day": day, "hour": hour}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == expected_count


@pytest.mark.parametrize(
    "ids, params",
    [
        ([1], {"page": 1}),
        ([2], {"page": 2}),
    ],
)
async def test_get_active_user_habits(
    ac, ids: list[int], params: dict[str, int]
):
    response = await ac.get(
        "/habits", params={"per_page": 1, **params}
    )
    assert response.status_code == 200
    data = response.json()
    assert ids == [habit["id"] for habit in data["items"]]
    assert data["pages"] == 2
    assert data["total_count"] == 2


async def test_get_habit_by_id(ac):
    response = await ac.get("/habits/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Утренняя зарядка"
    assert data["purpose"] == "Быть бодрым"
    assert set(data["days"]) == {
        Weekday.MONDAY.value,
        Weekday.TUESDAY,
    }
    assert set(data["hours"]) == {7, 8}
    assert data["completed"] == 1
    assert data["total"] == 2
    assert data["performance"] == 50


async def test_create_habit(ac):
    payload = {
        "name": "Вечерняя прогулка",
        "purpose": "Отдых",
        "days": [Weekday.FRIDAY.value, Weekday.SATURDAY],
        "hours": [19, 20],
    }
    response = await ac.post("/habits", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert set(data["days"]) == set(payload["days"])
    assert set(data["hours"]) == set(payload["hours"])


async def test_update_habit(ac):
    payload = {
        "name": "Обновленная зарядка",
        "purpose": "Быть бодрым всегда",
        "days": [Weekday.MONDAY],
        "hours": [6],
    }
    response = await ac.patch("/habits/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert set(data["days"]) == set(payload["days"])
    assert set(data["hours"]) == set(payload["hours"])


async def test_delete_habit(ac):
    response = await ac.delete("/habits/2")
    assert response.status_code == 200
    data = response.json()
    assert "pages" in data


async def test_mark_habit(ac):
    payload = {
        "reminder_date": "2024-06-01",
        "reminder_hour": 7,
        "is_completed": True,
    }
    response = await ac.post("/habits/1/mark", json=payload)
    assert response.status_code == 200
    response2 = await ac.get("/habits/1")
    data = response2.json()
    assert data["completed"] == 2
    assert data["total"] == 3
    assert data["performance"] == 66


async def test_mark_habit_already_marked(ac):
    payload = {
        "reminder_date": "2025-08-04",
        "reminder_hour": 7,
        "is_completed": False,
    }
    response = await ac.post("/habits/1/mark", json=payload)
    assert response.status_code == 409


async def test_mark_habit_not_found(ac):
    payload = {
        "reminder_date": "2024-06-01",
        "reminder_hour": 7,
        "is_completed": True,
    }
    response = await ac.post("/habits/99999/mark", json=payload)
    assert response.status_code == 404


async def test_get_statistics(ac):
    response = await ac.get("/habits/statistics")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 7
    assert [1] * 7 == [habit["total"] for habit in data["items"]]
