from aiogram_dialog import DialogManager

from core.exc import DataIsOutdated


def check_items_count(
    dialog_manager: DialogManager,
    total_count: int,
    can_be_equal: bool,
) -> None:
    if can_be_equal:
        if len(dialog_manager.dialog_data["tasks"]) > total_count:
            raise DataIsOutdated
    else:
        if len(dialog_manager.dialog_data["tasks"]) >= total_count:
            raise DataIsOutdated
