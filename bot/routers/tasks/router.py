from aiogram import Router
from aiogram.types import CallbackQuery
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.tasks import TaskCbData

from .repository import repository

router = Router(name=__name__)


@router.callback_query(TaskCbData.filter())
async def mark_task_completed(
    callback: CallbackQuery,
    callback_data: TaskCbData,
    client: AsyncClient,
    session_without_commit: AsyncSession,
):
    await repository.mark_item_as_reminder(
        callback=callback,
        session=session_without_commit,
        client=client,
        callback_data=callback_data,
    )
