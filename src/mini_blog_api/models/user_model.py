from typing import Optional
from pydantic import Field
from datetime import datetime

from .base_model import BaseModel, ObjectIdStr


class User(BaseModel):
    username: str = Field(title="User Name")
    password: str = Field(title="Password", min_length=6)
    email: str = Field(title="User's email address")

    class Config:
        populate_by_name = True
