from aiogram import Router
from src.begemot.handlers.admin import router as admin_router
from src.begemot.handlers.birthdays import router as birthdays_router
from src.begemot.handlers.common import router as common_router
from src.begemot.handlers.feedback import router as feedback_router
from src.begemot.handlers.registration import router as registration_router
from src.begemot.handlers.start import router as start_router
from src.begemot.handlers.wishlist import router as wishlist_router


def get_all_routers() -> list[Router]:
    return [
        start_router,
        registration_router,
        wishlist_router,
        birthdays_router,
        feedback_router,
        admin_router,
        common_router,
    ]
