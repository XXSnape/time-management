from core.models import Habit

from sqladmin import ModelView


class HabitAdmin(ModelView, model=Habit):
    column_list = "__all__"
