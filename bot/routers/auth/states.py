from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    login_or_registration = State()
    register_username = State()
    login_username = State()
    register_password = State()
    login_password = State()
