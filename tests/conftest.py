import pytest
from httpx import AsyncClient

from mini_blog_api.config import Settings, get_settings
from mini_blog_api.main import MiniBlogAPI, create_app


def get_test_settings() -> Settings:
    """Returns settings to use in testing."""
    settings: Settings = Settings()

    settings.db_uri = "mongodb://localhost:27017/test_mini_blog_db"

    return settings


@pytest.fixture
async def client():
    app: MiniBlogAPI = create_app()
    app.dependency_overrides[get_settings] = get_test_settings

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
