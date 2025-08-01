from aiogram.fsm.state import StatesGroup, State


class CreateTaskStates(StatesGroup):
    name = State()
    description = State()
    date = State()
    hour = State()
    notification_hour = State()


class ViewTaskStates(StatesGroup):
    view_all = State()
    view_details = State()
    delete_task = State()
    edit_task = State()
    edit_name = State()
