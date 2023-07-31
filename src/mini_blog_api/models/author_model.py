from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from pydantic import Field

from .base_model import BaseModel


class AuthorPayload(BaseModel):
    username: str = Field(title="Author Name")


class Author(BaseModel):
    id: Optional[ObjectId] = Field(title="Author Object ID", alias="_id")
    username: str = Field(title="Author Name")
    password: str = Field(title="Password")
    created_at: datetime = Field(title="Created Timestamp")
    updated_at: datetime = Field(title="Updated Timestamp")
