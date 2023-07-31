from typing import Optional
from pydantic import Field
from bson.objectid import ObjectId
from datetime import datetime

from .base_model import BaseModel

class CategoryPayload(BaseModel):
    name: str = Field(title="Category Name")
    description: Optional[str] = Field(title="Description")


class Category(BaseModel):
    id: Optional[ObjectId] = Field(title="Category Object Id", alias="_id")
    name: str = Field(title="Category Name")
    description: Optional[str] = Field(title="Description")
    created_at: datetime = Field(title="Created Timestamp")
    updated_at: datetime = Field(title="Updated Timestamp")