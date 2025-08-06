from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from core.enums import Methods
from core.utils.request import make_request, make_request_by_admin
from aiogram.utils.i18n import gettext as _


def activate_or_deactivate_bot(is_active: bool):
    async def _wrapper(
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ):
        client = dialog_manager.middleware_data["client"]
        await make_request_by_admin(
            client=client,
            endpoint=f"users/{callback.from_user.id}",
            method=Methods.patch,
            json={"is_active": is_active},
        )
        if is_active:
            text = _(
                "✅Бот будет присылать напоминания о задачах и привычках"
            )
        else:
            text = _(
                "❌Бот больше не будет присылать напоминания о задачах и привычках"
            )
        await dialog_manager.done()
        await callback.answer(text, show_alert=True)

    return _wrapper
