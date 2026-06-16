from src.targeting_service.model.links.base import AdminBase
from src.targeting_service.model.links.distribution_tag_link import (
    distribution_tag_table,
)
from src.targeting_service.model.links.recipient_tag_link import (
    recipient_tag_table,
)

__all__ = [
    "AdminBase",
    "distribution_tag_table",
    "recipient_tag_table",
]
