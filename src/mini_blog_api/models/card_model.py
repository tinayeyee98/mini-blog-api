from typing import Optional
from enum import Enum, unique
from pydantic import Field
from bson.objectid import ObjectId
from datetime import datetime

from .base_model import BaseModel


@unique
class CardStatusLabel(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    PENDING = "pending"
    FEATURED = "featured"
    DELETED = "deleted"


class CardPayload(BaseModel):
    name: str = Field(title="Card Name")
    status: CardStatusLabel = Field(title="Card Status")
    category: str = Field(title="Card's Category")
    author: str = Field(title="Author Name")
    content: str = Field(title="Content of the Card")


class CardPayloadCreate(BaseModel):
    name: str = Field(title="Card Name")
    status: CardStatusLabel = Field(title="Card Status")
    category: ObjectId = Field(title="Card's Category")
    author: ObjectId = Field(title="Author Name")
    content: str = Field(title="Content of the Card")
    

class Card(BaseModel):
    id: ObjectId = Field(title="Card Object ID", alias="_id")
    status: CardStatusLabel = Field(title="Card Status")
    category: ObjectId = Field(title="Card's Category Object ID")
    author: ObjectId = Field(title="Author Object ID")
    content: str = Field(title="Content of the Card")
    created_at: datetime = Field(title="Created Timestamp")
    updated_at: datetime = Field(title="Updated Timestamp")
