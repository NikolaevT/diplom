import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, relationship

from src.targeting_service.model.links import AdminBase, recipient_tag_table


class RecipientTable(AdminBase):
    """SQLAlchemy-модель таблицы recipient только для SQLAdmin (Peewee остаётся для логики)."""

    __tablename__ = "recipient"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = mapped_column(String(255), nullable=False)
    name = mapped_column(String(255), nullable=True)
    type = mapped_column(String(255), nullable=False)
    is_admin = mapped_column(Boolean(), default=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = mapped_column(String(255), nullable=True)
    updated_by = mapped_column(String(255), nullable=True)

    tags = relationship(
        "TagTable",
        secondary=recipient_tag_table,
        back_populates="recipients",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return self.name or str(self.telegram_id) or str(self.id)
