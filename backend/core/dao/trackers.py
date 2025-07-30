from core.models import Tracker
from .base import BaseDAO


class TrackersDAO(BaseDAO[Tracker]):
    model = Tracker
