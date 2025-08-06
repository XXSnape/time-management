from core.models import Timer
from sqladmin import ModelView


class TimerAdmin(ModelView, model=Timer):
    column_list = "__all__"
