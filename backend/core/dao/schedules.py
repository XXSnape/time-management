from core.models import Schedule

from .base import BaseDAO


class SchedulesDAO(BaseDAO[Schedule]):
    model = Schedule
