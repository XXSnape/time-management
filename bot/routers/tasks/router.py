from aiogram import Router
from aiogram.types import CallbackQuery
from httpx import AsyncClient, codes
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import Methods
from core.exc import ServerIsUnavailableExc
from core.keyboards.tasks import TaskCbData
from core.schemas.users import UserTelegramIdSchema
from core.utils.dt import get_moscow_dt
from core.utils.request import make_request
from database.dao.users import UsersDAO
from aiogram.utils.i18n import gettext as _


router = Router(name=__name__)


@router.callback_query(TaskCbData.filter())
async def mark_task_completed(
    callback: CallbackQuery,
    callback_data: TaskCbData,
    client: AsyncClient,
    session_without_commit: AsyncSession,
):
    user = await UsersDAO(
        session=session_without_commit
    ).find_one_or_none(
        UserTelegramIdSchema(telegram_id=callback.from_user.id)
    )
    try:
        await make_request(
            client=client,
            endpoint=f"tasks/{callback_data.task_id}/completion",
            method=Methods.patch,
            access_token=user.access_token,
            json={"date_of_completion": str(get_moscow_dt().date())},
        )
        await callback.answer(
            _("Задача успешно отмечена!"), show_alert=True
        )
    except ServerIsUnavailableExc as e:
        if e.response.status_code == codes.NOT_FOUND:
            await callback.answer(
                _("🙂Задача уже была отмечена"), show_alert=True
            )
        else:
            raise
    await callback.message.delete_reply_markup()
