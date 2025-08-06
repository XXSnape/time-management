from core.models import Tracker
from sqladmin import ModelView


class TrackerAdmin(ModelView, model=Tracker):
    column_list = "__all__"
