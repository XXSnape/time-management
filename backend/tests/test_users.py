from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User


async def test_sign_up(ac: AsyncClient, async_session: AsyncSession):
    response = await ac.post(
        "users/sign-up",
        json={
            "username": "newuser",
            "password": "newpass",
            "telegram_id": 222,
        },
    )
    assert response.status_code == 201
    assert "access_token" in response.json()
    result = await async_session.execute(
        select(User).where(User.username == "newuser")
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.telegram_id == 222
    assert user.is_active is True


async def test_sign_up_existing_username(ac: AsyncClient):
    response = await ac.post(
        "users/sign-up",
        json={
            "username": "user1",
            "password": "anypass",
            "telegram_id": 444,
        },
    )
    assert response.status_code == 409


async def test_sign_in(ac: AsyncClient):
    response = await ac.post(
        "/users/sign-in",
        json={"username": "user1", "password": "123"},
    )
    assert response.status_code == 201
    assert "access_token" in response.json()


async def test_sign_in_wrong_password(ac: AsyncClient):
    response = await ac.post(
        "/users/sign-in",
        json={"username": "user1", "password": "wrongpass"},
    )
    assert response.status_code == 401


async def test_check_username_for_existence(ac: AsyncClient):
    response = await ac.get("/users/user1")
    assert response.status_code == 200
    assert response.json()["result"] is True

    response = await ac.get("/users/nonexistentuser")
    assert response.json()["result"] is False


async def test_change_activity(
    ac: AsyncClient, async_session: AsyncSession
):
    response = await ac.patch(
        "/users/111", json={"is_active": False}
    )
    assert response.status_code == 200
    assert "result" in response.json()

    result = await async_session.execute(
        select(User).where(User.telegram_id == 111)
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.is_active is False


async def test_change_activity_not_found(ac: AsyncClient):
    response = await ac.patch(
        "/users/999999", json={"is_active": False}
    )
    assert response.status_code == 404
