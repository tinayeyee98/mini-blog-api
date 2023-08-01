# External Modules
from typing import List

import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Project Modules
from mini_blog_api.config import Settings, get_settings
from mini_blog_api.main import MiniBlogAPI, create_app
from mini_blog_api.repositories.auth_repository import AuthRepository
from mini_blog_api.repositories.db import get_db


def get_test_settings() -> Settings:
    """Returns settings to use in testing."""
    settings: Settings = Settings()

    settings.db_uri = "mongodb://localhost:27017"
    settings.db_name = f"test_{settings.db_name}"

    return settings


@pytest.fixture
def test_mini_blog_db():
    # get test settings
    settings: Settings = get_test_settings()

    # setup stage
    db_client: AsyncIOMotorClient = AsyncIOMotorClient(settings.db_uri)
    test_db: AsyncIOMotorDatabase = get_db(settings.db_uri, settings.db_name)
    AuthRepository.initialize(test_db)

    yield test_db
    db_client.close()


@pytest.fixture
async def client():
    app: MiniBlogAPI = create_app()
    app.dependency_overrides[get_settings] = get_test_settings

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
