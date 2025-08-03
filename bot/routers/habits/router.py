from aiogram import Router
from aiogram.types import CallbackQuery
from httpx import AsyncClient, codes
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import Methods
from core.exc import ServerIsUnavailableExc
from core.keyboards.habits import HabitCbData
from core.schemas.users import UserTelegramIdSchema
from core.utils.request import make_request
from database.dao.users import UsersDAO
from aiogram.utils.i18n import gettext as _


router = Router(name=__name__)


@router.callback_query(HabitCbData.filter())
async def mark_habit_completed_or_not(
    callback: CallbackQuery,
    callback_data: HabitCbData,
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
            endpoint=f"habits/{callback_data.habit_id}/mark",
            method=Methods.post,
            access_token=user.access_token,
            json={
                "reminder_date": callback_data.date,
                "reminder_hour": callback_data.hour,
                "is_completed": callback_data.completed,
            },
            delete_markup=False,
        )
        if callback_data.completed:
            await callback.answer(
                _("Привычка отмечена как выполненная!"),
                show_alert=True,
            )
        else:
            await callback.answer(
                _("Привычка отмечена как невыполненная!"),
                show_alert=True,
            )
    except ServerIsUnavailableExc as e:
        if e.response and e.response.status_code == codes.NOT_FOUND:
            await callback.answer(
                _("🙂Привычка уже была отмечена"), show_alert=True
            )
        else:
            raise
    await callback.message.delete_reply_markup()
