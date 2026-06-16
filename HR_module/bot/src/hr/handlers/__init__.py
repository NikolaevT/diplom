from src.hr.handlers.appointment_handler import router as appointment_handler_router
from src.hr.handlers.document_handler import router as document_handler_router
from src.hr.handlers.offer_handler import router as offer_handler_router
from src.hr.handlers.registration_handler import router as registration_router

__all__ = [
    "appointment_handler_router",
    "document_handler_router",
    "offer_handler_router",
    "registration_router",
]
