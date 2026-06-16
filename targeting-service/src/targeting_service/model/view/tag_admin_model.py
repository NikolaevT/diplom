import uuid
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, relationship

from src.targeting_service.model.links import AdminBase, distribution_tag_table, recipient_tag_table


class TagTable(AdminBase):
    """SQLAlchemy-модель таблицы tag только для SQLAdmin (Peewee остаётся для логики)."""

    __tablename__ = "tag"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String(255), nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = mapped_column(String(255), nullable=True)
    updated_by = mapped_column(String(255), nullable=True)

    distributions = relationship(
        "DistributionTable",
        secondary=distribution_tag_table,
        back_populates="tags",
        lazy="selectin",
    )

    recipients = relationship(
        "RecipientTable",
        secondary=recipient_tag_table,
        back_populates="tags",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return self.name or str(self.id)
