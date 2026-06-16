from sqladmin import Admin

from src.targeting_service.admin.distribution import Distribution
from src.targeting_service.admin.recipient import Recipient
from src.targeting_service.admin.tag import Tag


def register_admin_views(admin: Admin) -> None:
    admin.add_view(Distribution)
    admin.add_view(Recipient)
    admin.add_view(Tag)
