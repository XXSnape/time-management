from .base import BaseDAO
from core.models import Schedule


class SchedulesDAO(BaseDAO[Schedule]):
    model = Schedule
