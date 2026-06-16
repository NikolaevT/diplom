from __future__ import annotations
from src.targeting_service.db import Distribution, DistributionTag, Recipient, RecipientTag
from peewee import *
from datetime import datetime
from typing import List, Optional

from src.targeting_service.db import db
from src.targeting_service.model.distribution_entity import DistributionEntity


class DistributionRepository:
    """
    Репозиторий рассылок.
    """

    def list(self) -> List[DistributionEntity]:
        return list(DistributionEntity.select())

    def get_by_bmc_distribution_id(self, bmc_distribution_id: str) -> Optional[DistributionEntity]:
        """Найти рассылку по bmc_distribution_id."""
        return DistributionEntity.get_or_none(
            DistributionEntity.bmc_distribution_id == bmc_distribution_id
        )

    def has_linked_recipients(self, bmc_distribution_id: str) -> bool:
        
        """Есть ли у рассылки получатели по тегам (distribution_tag + recipient_tag)."""
        query = (Distribution
                .select()
                .join(DistributionTag, on=(DistributionTag.distribution_id == Distribution.id))
                .join(RecipientTag, on=(RecipientTag.tag_id == DistributionTag.tag_id))
                .join(Recipient, on=(Recipient.id == RecipientTag.recipient_id))
                .where(Distribution.bmc_distribution_id == bmc_distribution_id))
    
        return query.exists()  


    def get_telegram_ids_by_bmc_distribution_id(self, bmc_distribution_id: str) -> List[str]: 
        """Список telegram_id получателей по тегам (distribution_tag + recipient_tag)."""
        query = (Recipient
                .select(Recipient.telegram_id)
                .join(RecipientTag, on=(RecipientTag.recipient_id == Recipient.id))
                .join(DistributionTag, on=(DistributionTag.tag_id == RecipientTag.tag_id))
                .join(Distribution, on=(Distribution.id == DistributionTag.distribution_id))
                .where(Distribution.bmc_distribution_id == bmc_distribution_id)
                .distinct())
    
        return [row.telegram_id for row in query]


    def create(self, entity: DistributionEntity) -> DistributionEntity:
        entity.save(force_insert=True)
        return entity

    def update(self, entity: DistributionEntity) -> DistributionEntity:
        entity.updated_at = datetime.utcnow()
        entity.save()
        return entity

    def delete_by_bmc_distribution_id(self, bmc_distribution_id: str) -> bool:
        n = (
            DistributionEntity.delete()
            .where(DistributionEntity.bmc_distribution_id == bmc_distribution_id)
            .execute()
        )
        return n > 0
