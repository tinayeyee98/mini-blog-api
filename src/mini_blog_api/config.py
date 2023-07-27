from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application runtime settings which can be configured via command line or .env file."""

    app_root_path: str = Field(
        default="", title="Application Root Path", description="ASGI root_path variable"
    )
    internal_routes_prefix: str = Field(
        default="/internal", title="Internal Routes Prefix"
    )
    healthcheck_response: str = Field(
        default="T0sK",
        title="Healthcheck Response",
        description="The response content for healthcheck requests",
    )
    db_url: str = Field(
        default="mongodb://localhost:27017/mini_blog_db", title="Database URL"
    )


    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
