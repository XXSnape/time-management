from aiogram.fsm.state import State, StatesGroup


class ActivityStates(StatesGroup):
    change = State()
