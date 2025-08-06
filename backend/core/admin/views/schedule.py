from core.models import Schedule

from sqladmin import ModelView


class ScheduleAdmin(ModelView, model=Schedule):
    column_list = "__all__"
