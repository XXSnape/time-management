from aiogram.fsm.state import StatesGroup, State


class CreateTaskStates(StatesGroup):
    name = State()
    date = State()
