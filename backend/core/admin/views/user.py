from core.models import User
from sqladmin import ModelView


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.telegram_id,
        User.is_admin,
    ]
    column_details_exclude_list = [User.password]
    form_excluded_columns = [User.password]
    can_delete = False
