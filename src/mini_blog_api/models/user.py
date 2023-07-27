from pydantic import Field
from datetime import datetime

from .base_model import BaseModel, ObjectIdStr


class User(BaseModel):
    id: ObjectIdStr = Field(title="User Object ID", alias="_id")
    username: str = Field(title="User Name")
    password: str = Field(title="Password", min_length=6)
    email: str = Field(title="User's email address")
    created_at: datetime = Field(title="Record created timestamp")
    updated_at: datetime = Field(title="Record updated timestamp")

    class Config:
        allow_population_by_field_name = True
