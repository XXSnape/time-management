from aiogram.fsm.state import StatesGroup, State


class ActivityStates(StatesGroup):
    change = State()
