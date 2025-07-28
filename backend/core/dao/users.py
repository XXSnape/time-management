from .base import BaseDAO
from core.models import User


class UsersDao(BaseDAO[User]):
    model = User
