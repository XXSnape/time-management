from aiogram.fsm.state import State, StatesGroup


class CreateHabitStates(StatesGroup):
    name = State()
    purpose = State()
    days = State()
    hours = State()


class HabitsManagementStates(StatesGroup):
    view_all = State()
    view_details = State()
    delete = State()
    edit = State()
    edit_name = State()
    edit_purpose = State()
    edit_days = State()
    edit_hours = State()
    mark = State()
