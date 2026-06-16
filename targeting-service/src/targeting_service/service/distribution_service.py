from __future__ import annotations

from typing import List

from fastapi import HTTPException, status
from httpx import HTTPStatusError
from src.targeting_service.db import db
from src.targeting_service.dto.distribution_dto import (
    DistributionDto,
    DistributionListDto,
    DistributionUpdate,
)
from src.targeting_service.mapper.disrtibutoin_mapper import DistributionMapper
from src.targeting_service.repository.distribution_repository import DistributionRepository
from src.targeting_service.service.bot_client import post_news




def list_distributions(repo: DistributionRepository) -> List[DistributionListDto]:
    """Получить список всех рассылок."""
    entities = repo.list()
    return [DistributionMapper.to_list_dto(e) for e in entities]


def get_distribution(
    repo: DistributionRepository, bmc_distribution_id: str
) -> DistributionDto | None:
    """Получить рассылку по bmc_distribution_id."""
    entity = repo.get_by_bmc_distribution_id(str(bmc_distribution_id))
    if entity is None:
        return None
    return DistributionMapper.to_dto(entity)


def create_distribution(repo: DistributionRepository, dto: DistributionDto) -> DistributionDto:
    """
    1. Проверить, есть ли у рассылки (bmc_distribution_id) получатели, связанные через теги (distribution_tag + recipient_tag).
    2. Если связи нет — сохраняем или обновляем рассылку в БД и возвращаем 422.
    3. Если связь есть — получаем список telegram_id получателей; если список пуст — 422.
    4. Отправляем пост в бота на /api/v1/news/ каждому получателю.
    """
    if not (dto.bmc_distribution_id and dto.bmc_distribution_id.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Required field is missing: bmcDistributionId",
        )
    if not dto.post or not (dto.post.content and dto.post.content.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Required field is missing: post.content",
        )
    has_recipients = repo.has_linked_recipients(str(dto.bmc_distribution_id))

    if not has_recipients:
        with db.atomic():
            existing = repo.get_by_bmc_distribution_id(str(dto.bmc_distribution_id))
            if existing is None:
                entity = DistributionMapper.to_entity(dto)
                repo.create(entity)
            else:
                existing.name = dto.name
                repo.update(existing)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No recipients linked to this distribution (bmc_distribution_id).",
        )

    telegram_ids = repo.get_telegram_ids_by_bmc_distribution_id(str(dto.bmc_distribution_id))
    if not telegram_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No chat IDs found to send the news.",
        )

    for telegram_id in telegram_ids:
        try:
            post_news(dto.post, telegram_id)
        except HTTPStatusError as e:
            detail: str | None = None
            if e.response is not None:
                try:
                    json_body = e.response.json()
                    detail = json_body.get("detail")
                except Exception:
                    detail = e.response.text

            if not detail:
                detail = "Failed to send news to at least one chat."

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail,
            ) from e
    return dto


def update_distribution(
    repo: DistributionRepository,
    bmc_distribution_id: str,
    payload: DistributionUpdate,
) -> DistributionDto | None:
    """Обновить рассылку по bmc_distribution_id."""
    with db.atomic():
        entity = repo.get_by_bmc_distribution_id(str(bmc_distribution_id))
        if entity is None:
            return None

        entity.name = payload.name
        saved = repo.update(entity)
    return DistributionMapper.to_dto(saved)


def delete_distribution(repo: DistributionRepository, bmc_distribution_id: str) -> bool:
    """Удалить рассылку по bmc_distribution_id."""
    with db.atomic():
        return repo.delete_by_bmc_distribution_id(str(bmc_distribution_id))
