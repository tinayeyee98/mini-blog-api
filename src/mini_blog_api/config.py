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
    api_prefix: str = Field(
        default="/api/v1",
        title="API Prefix"
    )
    db_uri: str = Field(
        default="mongodb://localhost:27017/", title="Database URI"
    )
    db_name: str = Field(
        default="mini_blog_db", title="DB Name"
    )
    password_length: int = Field(
        default=12, title="Random generate password length"
    )
    jwt_secret: str = Field(
        default="miniblogtokensecret", title="JWT Token Secret"
    )
    jwt_alg: str = Field(
        default="HS256", title="JWT Algorithm"
    )
    token_exp: int = Field(
        default=300, title="Token Expiration"
    )


    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
