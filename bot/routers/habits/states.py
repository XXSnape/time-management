from aiogram.fsm.state import StatesGroup, State


class CreateHabitStates(StatesGroup):
    name = State()
    purpose = State()
    days = State()
    hours = State()
