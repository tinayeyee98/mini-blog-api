from typing import Optional
from pydantic import Field
from bson.objectid import ObjectId
from datetime import datetime

from .base_model import BaseModel


class UserPayload(BaseModel):
    username: str = Field(title="User Name")


class User(BaseModel):
    id: Optional[ObjectId] = Field(title="User Object ID", alias="_id")
    username: str = Field(title="User Name")
    password: str = Field(title="Password")
    created_at: datetime = Field(title="Created Timestamp")
    updated_at: datetime = Field(title="Updated Timestamp")
