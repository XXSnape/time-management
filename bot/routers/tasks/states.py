from aiogram.fsm.state import StatesGroup, State


class CreateTaskStates(StatesGroup):
    name = State()
    description = State()
    date = State()
    hour = State()
    notification_hour = State()


class TasksManagementStates(StatesGroup):
    view_all = State()
    view_details = State()
    delete = State()
    edit = State()
    edit_name = State()
    edit_description = State()
    edit_deadline_date = State()
    edit_deadline_time = State()
    edit_hour = State()
    mark = State()
