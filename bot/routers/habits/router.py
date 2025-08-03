from aiogram import Router
from aiogram.types import CallbackQuery
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.habits import HabitCbData
from .repository import repository

router = Router(name=__name__)


@router.callback_query(HabitCbData.filter())
async def mark_habit_completed_or_not(
    callback: CallbackQuery,
    callback_data: HabitCbData,
    client: AsyncClient,
    session_without_commit: AsyncSession,
):
    await repository.mark_item_as_reminder(
        callback=callback,
        session=session_without_commit,
        client=client,
        callback_data=callback_data,
    )
