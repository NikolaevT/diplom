"""Таблица связи many-to-many: рассылки <-> теги."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID

from src.targeting_service.model.links.base import AdminBase

distribution_tag_table = Table(
    "distribution_tag",
    AdminBase.metadata,
    Column(
        "distribution_id",
        UUID(as_uuid=True),
        ForeignKey("distribution.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", UUID(as_uuid=True), ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    Column("created_by", String(255), nullable=True),
    Column("updated_by", String(255), nullable=True),
)
