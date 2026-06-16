"""Таблица связи many-to-many: теги <-> получатели."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID

from src.targeting_service.model.links.base import AdminBase

recipient_tag_table = Table(
    "recipient_tag",
    AdminBase.metadata,
    Column(
        "tag_id", UUID(as_uuid=True), ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "recipient_id",
        UUID(as_uuid=True),
        ForeignKey("recipient.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    Column("created_by", String(255), nullable=True),
    Column("updated_by", String(255), nullable=True),
)
