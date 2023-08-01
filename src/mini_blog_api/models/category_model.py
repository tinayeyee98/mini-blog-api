from datetime import datetime
from typing import Optional

from bson.objectid import ObjectId
from fastapi import Query
from pydantic import Field

from .base_model import BaseModel


class CategoryQueryParams(BaseModel):
    skip: Optional[int] = Query(default=0)
    limit: Optional[int] = Query(default=100)
    id: Optional[str] = Query(default=None)
    name: Optional[str] = Query(default=None)


class CategoryPayload(BaseModel):
    name: str = Field(title="Category Name")
    description: Optional[str] = Field(title="Description")


class Category(BaseModel):
    id: Optional[ObjectId] = Field(title="Category Object Id", alias="_id")
    name: str = Field(title="Category Name")
    description: Optional[str] = Field(title="Description")
    created_at: datetime = Field(title="Created Timestamp")
    updated_at: datetime = Field(title="Updated Timestamp")
