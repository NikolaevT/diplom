from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from src.targeting_service.config import settings
from src.targeting_service.controller.admin_controller import router as admin_api_router
from src.targeting_service.controller import api_router
from src.targeting_service.controller.distribution_controller import router as distribution_router
from src.targeting_service.db import db
from src.targeting_service.logging_config import setup_logging
from src.targeting_service.repository.distribution_repository import DistributionRepository
from sqladmin import Admin
from src.targeting_service.admin import register_admin_views
from src.targeting_service.model.admin_engine import engine
from src.targeting_service.migrate import run_migrations
from sqladmin.helpers import slugify_class_name


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan события приложения."""
    logger.info("🚀 Приложение запускается...")
    logger.info(f"Название: {settings.app_name}")
    logger.info(f"Порт: {settings.port}")
    logger.info(f"Уровень логирования: {settings.log_level}")
    run_migrations()
    db.connect(reuse_if_open=True)
    app.state.distribution_repository = DistributionRepository()

    yield

    if not db.is_closed():
        db.close()
    logger.info("🛑 Приложение останавливается...")


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    """Не заполнены обязательные поля — возвращаем 400."""
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


app.include_router(distribution_router)
app.include_router(api_router)
app.include_router(admin_api_router)

admin = Admin(
    app,
    engine=engine,
    templates_dir="src/targeting_service/templates",
)


def get_identity_for_obj(obj):
    for view in admin.views:
        if hasattr(view, "model") and view.model is obj.__class__:
            return view.identity
    return slugify_class_name(obj.__class__.__name__)


admin.templates.env.globals["get_identity_for_obj"] = get_identity_for_obj

register_admin_views(admin)


@app.get("/health")
def health() -> dict[str, str]:
    logger.info("Health check запрос")
    return {"status": "ok"}


def main() -> None:
    setup_logging(log_level=settings.log_level)
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
    )
