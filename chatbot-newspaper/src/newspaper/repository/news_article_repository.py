from src.newspaper.model import NewsArticleEntity


def save(model: NewsArticleEntity) -> NewsArticleEntity:
    model.save()
    return model
