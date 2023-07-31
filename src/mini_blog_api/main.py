import structlog
from fastapi import FastAPI
from typing import Any, Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from .__init__ import __name__ as app_name
from .__init__ import __version__ as app_version
from .config import Settings, get_settings
from .middleware import configure_middleware
from .models.base_model import AppInfo
from .controllers import(
    author_controller,
    internal_controller, 
    category_controller, 
    card_controller,
) 
from .repositories.db import get_db
from .repositories.author_repository import UserRepository
from .repositories.category_repository import CategoryRepository
from .repositories.card_repository import CardRepository

log: structlog.BoundLogger = structlog.get_logger()
settings: Settings = get_settings()


class MiniBlogAPI(FastAPI):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


async def startup() -> None:
    log.msg("application startup complete")


async def shutdown() -> None:
    log.msg("application is shutting down")


def create_app(
        app_name: str = app_name, app_version: str = app_version
) -> MiniBlogAPI:
    app = MiniBlogAPI(
        root_path=settings.app_root_path,
        title=app_name,
        version=app_version,
    )
    init_db()  # Initialize Database

    # Initial variable to incliude extra information for openapi tags
    openapi_tags: List[Dict[str, Any]] = []

    # Routes and additional information for openapi
    app.info = AppInfo(app_name=app.title, app_version=app.version)
    app.include_router(internal_controller.router,
                       prefix=settings.internal_routes_prefix)
    openapi_tags.extend(internal_controller.openapi_tags)
    app.include_router(author_controller.router, prefix=settings.api_prefix)
    app.include_router(category_controller.router, prefix=settings.api_prefix)
    app.include_router(card_controller.router, prefix=settings.api_prefix)


    # Additional information for openapi docs
    app.openapi_tags = openapi_tags

    # HTTP filters
    configure_middleware(app)

    # Register application lifecycle envents
    app.add_event_handler("startup", startup)
    app.add_event_handler("shutdown", shutdown)
    return app


def init_db(db_uri: str = settings.db_uri, db_name: str = settings.db_name):
    db: AsyncIOMotorDatabase = get_db(db_uri, db_name)
    UserRepository.initialize(db=db)
    CategoryRepository.initialize(db=db)
    CardRepository.initialize(db=db)
