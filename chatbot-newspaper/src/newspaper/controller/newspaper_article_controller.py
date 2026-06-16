from fastapi import APIRouter

from src.newspaper.dto import NewsArticleDto
from src.newspaper.service.news_article_service import  receive

router = APIRouter(
    prefix="/api/v1/news",
    tags=["newspaper"],
    # dependencies=[Depends(require_jwt)],
)


@router.post("")
async def receive_news(newspaper: NewsArticleDto):
    return await receive(newspaper)

