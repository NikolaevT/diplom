from src.targeting_service.dto.distribution_dto import DistributionDto, DistributionListDto
from src.targeting_service.model.distribution_entity import DistributionEntity


class DistributionMapper:
    """
    Маппер для преобразования Distribution DTO <-> DistributionEntity.

    """

    @staticmethod
    def to_entity(dto: DistributionDto) -> DistributionEntity:
        return DistributionEntity(
            bmc_distribution_id=str(dto.bmc_distribution_id),
            name=dto.name,
        )

    @staticmethod
    def to_dto(entity: DistributionEntity) -> DistributionDto:
        return DistributionDto(
            bmc_distribution_id=str(entity.bmc_distribution_id),
            name=entity.name or "",
        )

    @staticmethod
    def to_list_dto(entity: DistributionEntity) -> DistributionListDto:
        return DistributionListDto(
            bmc_distribution_id=str(entity.bmc_distribution_id),
            name=entity.name or "",
        )
