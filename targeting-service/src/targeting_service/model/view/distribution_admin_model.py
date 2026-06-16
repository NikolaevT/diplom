import uuid
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, relationship

from src.targeting_service.model.links import AdminBase, distribution_tag_table


class DistributionTable(AdminBase):
    """SQLAlchemy-модель таблицы distribution только для SQLAdmin (Peewee остаётся для логики)."""

    __tablename__ = "distribution"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String(255), nullable=False)
    bmc_distribution_id = mapped_column(String(255), unique=True, nullable=False)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = mapped_column(String(255), nullable=True)
    updated_by = mapped_column(String(255), nullable=True)

    tags = relationship(
        "TagTable",
        secondary=distribution_tag_table,
        back_populates="distributions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return self.name
