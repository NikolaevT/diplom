from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.targeting_service.dto.distribution_dto import (
    DistributionDto,
    DistributionListDto,
    DistributionUpdate,
)
from src.targeting_service.deps import (
    ensure_db,
    ensure_valid_token,
    get_distribution_repository,
)
from src.targeting_service.repository.distribution_repository import DistributionRepository
from src.targeting_service.service import distribution_service

router = APIRouter(prefix="/api/v1/distribution", tags=["distribution"])


@router.get(
    "",
    response_model=list[DistributionListDto],
    summary="Получить список рассылок",
)
def get_distributions(
    repo: DistributionRepository = Depends(get_distribution_repository),
    _: None = Depends(ensure_db),
) -> list[DistributionListDto]:
    """Получить список всех рассылок."""
    return distribution_service.list_distributions(repo)


@router.post(
    "",
    response_model=DistributionDto,
    summary="Создать рассылку или отправить пост в бота",
)
def create_or_update_distribution(
    payload: DistributionDto,
    repo: DistributionRepository = Depends(get_distribution_repository),
    _: None = Depends(ensure_db),
    __: None = Depends(ensure_valid_token),
) -> DistributionDto:
    """
    Если нет связи bmc_distribution_id ↔ получатели — сохранить в БД.
    Если связь есть — отправить пост в бота на /api/v1/news/.
    """
    return distribution_service.create_distribution(repo, payload)


@router.put(
    "/{bmc_distribution_id}",
    response_model=DistributionDto,
    summary="Изменить рассылку по bmc_distribution_id",
)
def update_distribution(
    bmc_distribution_id: str,
    payload: DistributionUpdate,
    repo: DistributionRepository = Depends(get_distribution_repository),
    _: None = Depends(ensure_db),
) -> DistributionDto:
    """Изменить существующую рассылку по bmc_distribution_id."""
    result = distribution_service.update_distribution(repo, bmc_distribution_id, payload)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Distribution not found",
        )
    return result


@router.delete(
    "/{bmc_distribution_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить рассылку по bmc_distribution_id",
)
def delete_distribution(
    bmc_distribution_id: str,
    repo: DistributionRepository = Depends(get_distribution_repository),
    _: None = Depends(ensure_db),
) -> None:
    """Удалить рассылку по bmc_distribution_id."""
    deleted = distribution_service.delete_distribution(repo, bmc_distribution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Distribution not found",
        )
