from fastapi import APIRouter

from src.targeting_service.controller.recipient_controller import router as recipient_router


api_router = APIRouter()

api_router.include_router(recipient_router)
