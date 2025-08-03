from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, ManagedMultiselect
from httpx import AsyncClient, codes
from sqlalchemy.ext.asyncio import AsyncSession

from core.enums import Resources, Methods
from core.schemas.users import UserTelegramIdSchema
from core.utils.dt import get_moscow_dt
from core.utils.request import make_request
from database.dao.users import UsersDAO
from abc import ABC, abstractmethod
from aiogram_dialog import DialogManager
from core.exc import DataIsOutdated, ServerIsUnavailableExc
from aiogram.utils.i18n import gettext as _


class BaseRepository(ABC):
    resource: Resources
    states: StatesGroup

    @property
    @abstractmethod
    def completed(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def deleted(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def item_been_marked(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_texts_by_items(
        self, items: list[dict]
    ) -> list[list[str | int]]:
        raise NotImplementedError

    @abstractmethod
    def generate_item_info(
        self,
        dialog_manager: DialogManager,
        item: dict,
        item_id: str | int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def make_request_to_mark_as_reminder(
        self,
        client: AsyncClient,
        callback_data: CallbackData,
        callback: CallbackQuery,
        access_token: str,
    ):
        raise NotImplementedError

    async def mark_item_as_reminder(
        self,
        callback: CallbackQuery,
        session: AsyncSession,
        client: AsyncClient,
        callback_data: CallbackData,
    ):
        user = await UsersDAO(session=session).find_one_or_none(
            UserTelegramIdSchema(telegram_id=callback.from_user.id)
        )
        try:
            await self.make_request_to_mark_as_reminder(
                client=client,
                callback_data=callback_data,
                access_token=user.access_token,
                callback=callback,
            )
        except ServerIsUnavailableExc as e:
            if e.response and e.response.status_code in (
                codes.NOT_FOUND,
                codes.CONFLICT,
            ):
                await callback.answer(
                    self.item_been_marked, show_alert=True
                )
            else:
                raise
        await callback.message.delete_reply_markup()

    @staticmethod
    async def get_client_session_token(
        dialog_manager: DialogManager,
    ) -> tuple[AsyncClient, AsyncSession, str]:
        client: AsyncClient = dialog_manager.middleware_data[
            "client"
        ]
        session: AsyncSession = dialog_manager.middleware_data[
            "session_without_commit"
        ]
        user = await UsersDAO(session=session).find_one_or_none(
            UserTelegramIdSchema(
                telegram_id=dialog_manager.event.from_user.id
            )
        )
        return client, session, user.access_token

    @staticmethod
    def check_items_count(
        dialog_manager: DialogManager,
        total_count: int,
        can_be_equal: bool,
    ) -> None:
        if can_be_equal:
            if (
                len(dialog_manager.dialog_data["items"])
                > total_count
            ):
                raise DataIsOutdated
        else:
            if (
                len(dialog_manager.dialog_data["items"])
                >= total_count
            ):
                raise DataIsOutdated

    @staticmethod
    def get_index_from_cache(
        texts: list[list[int | str]], item_id: int
    ) -> int:
        to_delete_index = None
        for index, (__, id_) in enumerate(texts):
            if id_ == item_id:
                to_delete_index = index
                break
        return to_delete_index

    async def get_user_resources(
        self,
        dialog_manager: DialogManager,
        **kwargs,
    ):
        load_more = _("Загрузить еще")
        items_text = _("Нажмите, чтобы посмотреть подробности")
        back_to_view = _("Вернуться к выбору")
        items_from_cache = dialog_manager.dialog_data.get("items")
        scrolling_group_id = f"all_{self.resource}"
        if items_from_cache is not None:
            scrolling_group = dialog_manager.find(scrolling_group_id)
            pages_count = await scrolling_group.get_page_count(
                dialog_manager.dialog_data
            )
            current_page = await scrolling_group.get_page()

            can_be_loaded = current_page == pages_count - 1 and len(
                items_from_cache
            ) < dialog_manager.dialog_data.get("total_count")
            return {
                "items_text": items_text,
                "items": items_from_cache,
                "can_be_loaded": can_be_loaded,
                "load_more": load_more,
                "back": back_to_view,
            }
        client, session, access_token = (
            await self.get_client_session_token(dialog_manager)
        )
        result = await make_request(
            client=client,
            endpoint=self.resource,
            method=Methods.get,
            access_token=access_token,
        )
        texts = self.get_texts_by_items(result["items"])
        dialog_manager.dialog_data.update(
            total_count=result["total_count"],
            next_page=2,
            items=texts,
        )
        return {
            "items_text": items_text,
            "items": texts,
            "can_be_loaded": False,
            "load_more": load_more,
            "back": back_to_view,
        }

    async def upload_more_items(
        self,
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ):
        client, session, access_token = (
            await self.get_client_session_token(dialog_manager)
        )
        result = await make_request(
            client=client,
            endpoint=self.resource,
            method=Methods.get,
            access_token=access_token,
            params={"page": dialog_manager.dialog_data["next_page"]},
        )
        self.check_items_count(
            dialog_manager=dialog_manager,
            total_count=result["total_count"],
            can_be_equal=False,
        )
        count = result["total_count"] - len(
            dialog_manager.dialog_data["items"]
        )
        new_texts = self.get_texts_by_items(result["items"][-count:])
        dialog_manager.dialog_data.update(
            last_loaded_page=dialog_manager.dialog_data["next_page"]
            + 1,
            items=dialog_manager.dialog_data["items"] + new_texts,
        )

    async def on_click_item(
        self,
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
        item_id: str,
    ) -> None:
        item_data = dialog_manager.dialog_data.get(
            f"item_{item_id}_data"
        )
        if item_data:
            await dialog_manager.next()
            return
        client, session, access_token = (
            await self.get_client_session_token(dialog_manager)
        )
        item = await make_request(
            client=client,
            endpoint=f"{self.resource}/{item_id}",
            method=Methods.get,
            access_token=access_token,
        )
        self.generate_item_info(
            dialog_manager=dialog_manager,
            item=item,
            item_id=item_id,
        )
        await dialog_manager.next()

    async def _delete_item_from_view(
        self,
        callback: CallbackQuery,
        dialog_manager: DialogManager,
        to_mark: bool,
    ) -> None:
        client, session, access_token = (
            await self.get_client_session_token(dialog_manager)
        )

        item_id = dialog_manager.dialog_data["current_item"]
        method = Methods.patch if to_mark else Methods.delete
        end_of_endpoint = "/completion" if to_mark else ""
        json = (
            {"date_of_completion": str(get_moscow_dt().date())}
            if to_mark
            else None
        )
        items_count = await make_request(
            client=client,
            endpoint=f"{self.resource}/{item_id}{end_of_endpoint}",
            method=method,
            access_token=access_token,
            json=json,
        )
        texts = dialog_manager.dialog_data["items"]
        to_delete_index = self.get_index_from_cache(
            texts=texts, item_id=item_id
        )
        texts.pop(to_delete_index)
        if not to_mark:
            text = self.deleted
        else:
            text = self.completed

        await callback.answer(text, show_alert=True)
        self.check_items_count(
            dialog_manager=dialog_manager,
            total_count=items_count["total_count"],
            can_be_equal=True,
        )
        if (
            items_count["pages"]
            < dialog_manager.dialog_data["next_page"]
        ):
            dialog_manager.dialog_data["next_page"] = items_count[
                "pages"
            ]
        dialog_manager.dialog_data["total_count"] = items_count[
            "total_count"
        ]
        await dialog_manager.switch_to(self.states.view_all)

    async def delete_item(
        self,
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await self._delete_item_from_view(
            callback=callback,
            dialog_manager=dialog_manager,
            to_mark=False,
        )

    async def mark_item(
        self,
        callback: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
    ) -> None:
        await self._delete_item_from_view(
            callback=callback,
            dialog_manager=dialog_manager,
            to_mark=True,
        )

    async def _change_item_and_go_next(
        self,
        dialog_manager: DialogManager,
        item: str,
        value: str | int | list[str | int],
    ) -> None:
        client, session, access_token = (
            await self.get_client_session_token(dialog_manager)
        )
        item_id = dialog_manager.dialog_data["current_item"]
        item = await make_request(
            client=client,
            endpoint=f"{self.resource}/{item_id}",
            method=Methods.patch,
            json={item: value},
            access_token=access_token,
        )
        texts = self.get_texts_by_items([item])

        index_to_replace = self.get_index_from_cache(
            texts=dialog_manager.dialog_data["items"],
            item_id=item_id,
        )
        dialog_manager.dialog_data["items"][index_to_replace] = (
            texts[0]
        )
        self.generate_item_info(
            dialog_manager=dialog_manager, item=item, item_id=item_id
        )
        await dialog_manager.switch_to(self.states.view_details)

    def change_attr_by_text(self, attr: str):
        async def _wrapper(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            text: str,
        ):
            await self._change_item_and_go_next(
                dialog_manager=dialog_manager,
                item=attr,
                value=text,
            )

        return _wrapper

    def cancel_multiselect(self, multiselect_id: str):
        async def _wrapper(
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
        ):
            multiselect: ManagedMultiselect = dialog_manager.find(
                multiselect_id
            )
            await multiselect.reset_checked()
            dialog_manager.dialog_data.pop("is_first_viewing")
            await dialog_manager.switch_to(self.states.edit)

        return _wrapper

    def change_attr_by_multiselect(
        self, attr: str, multiselect_id: str
    ):
        async def _wrapper(
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
        ):
            multiselect: ManagedMultiselect = dialog_manager.find(
                multiselect_id
            )
            checkbox = multiselect.get_checked()
            dialog_manager.dialog_data.pop("is_first_viewing")
            await multiselect.reset_checked()
            await self._change_item_and_go_next(
                dialog_manager=dialog_manager,
                item=attr,
                value=checkbox,
            )

        return _wrapper

    @staticmethod
    async def get_item_details(
        dialog_manager: DialogManager,
        **kwargs,
    ):
        item_id = dialog_manager.dialog_data["current_item"]
        item_data = dialog_manager.dialog_data[
            f"item_{item_id}_data"
        ]
        item_text = item_data["text"]
        return {
            "item_text": item_text,
            "edit_text": _("Редактировать"),
            "delete_text": _("Удалить"),
            "back": _("Вернуться"),
        }
