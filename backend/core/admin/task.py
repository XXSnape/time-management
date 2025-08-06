from core.models import Task

from sqladmin import ModelView


class TaskAdmin(ModelView, model=Task):
    column_list = "__all__"
