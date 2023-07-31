# External Modules
from typing import List

import pytest
from httpx import AsyncClient
from pymongo import MongoClient
from pymongo.database import Database

# Project Modules
from mini_blog_api.config import Settings, get_settings
from mini_blog_api.main import MiniBlogAPI, create_app


def get_test_settings() -> Settings:
    """Returns settings to use in testing."""
    settings: Settings = Settings()

    settings.db_uri = "mongodb://localhost:27017/test_mini_blog_db"

    return settings


@pytest.fixture
def mini_blog_db():
    # get test settings
    settings: Settings = get_test_settings()
    # db collections for setup and teardown
    db_collection_names: List[str] = ["tests", "author", "category", "cards"]

    # setup stage
    db_client: MongoClient = MongoClient(settings.db_uri)
    test_db: Database = db_client.get_database()

    for collection in db_collection_names:
        test_db[collection].drop()

    yield test_db

    # teardown stage
    db_client.close()


@pytest.fixture
async def client():
    app: MiniBlogAPI = create_app()
    app.dependency_overrides[get_settings] = get_test_settings

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
