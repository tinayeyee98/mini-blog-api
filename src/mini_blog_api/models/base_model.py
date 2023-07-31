from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from bson.errors import InvalidId
from bson.objectid import ObjectId

from ..config import Settings, get_settings

settings: Settings = get_settings()

class BaseModel(PydanticBaseModel):
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ErrorMessage(BaseModel):
    detail: str = Field(title="Detail", description="Error information")


default_responses = {
    404: {
        "model": ErrorMessage,
        "title": "Not Found",
    },
    503: {
        "model": ErrorMessage,
        "title": "Service Temporarily Unavailable",
    },
}


class AppInfo(BaseModel):
    """Data model for application information."""

    app_name: str
    app_version: str
    healthcheck_response: str = Field(
        default=settings.healthcheck_response,
        title="Response data in base64 format for healthcheck request",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "oss_resourcesapi",
                "app_version": "1.0.0",
                "healthcheck_response": "T0sK",
            }
        }
