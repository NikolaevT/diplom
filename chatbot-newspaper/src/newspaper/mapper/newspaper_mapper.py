from src.newspaper.dto import NewsArticleDto
from src.newspaper.model import NewsArticleEntity


class NewsArticleMapper:
    @staticmethod
    def to_entity(dto: NewsArticleDto) -> NewsArticleEntity:
        """Конвертация из DTO в MongoEngine Entity"""
        return NewsArticleEntity(
            content=dto.content,
            source_url=dto.source_url,
            telegram_id=dto.telegram_id,
        )

    @staticmethod
    def to_dto(entity: NewsArticleEntity) -> NewsArticleDto:
        """Конвертация из MongoEngine Entity в DTO"""
        return NewsArticleDto(
            image_url=entity.source_url,
            content=entity.content,
            source_url=entity.source_url,
            telegram_id=entity.telegram_id,
        )
