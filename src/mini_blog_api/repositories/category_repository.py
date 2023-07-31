import json
from datetime import datetime
from typing import Any, Dict, List

import structlog
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo.errors import ServerSelectionTimeoutError

from ..models.category_model import Category, CategoryPayload
from ..services.util import sanitize

log = structlog.get_logger()


class CategoryRepository:
    @classmethod
    def initialize(cls, db: AsyncIOMotorClient) -> None:
        cls.collection = db["category"]

    @classmethod
    async def find_category(cls, name):
        try:
            category_dict: Dict[str, Any] = await cls.collection.find_one(
                dict(name=name)
            )
            if category_dict:
                return Category.model_validate(category_dict)

        except ServerSelectionTimeoutError as error:
            log.error(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def find_category_list(cls, query_filter: Dict[str, Any]) -> List[Category]:
        try:
            docs: List[Category] = []
            db_cursor: AsyncIOMotorCursor = cls.collection.find(query_filter)
            async for doc in db_cursor:
                docs.append(Category.model_validate(doc))
            return docs

        except ServerSelectionTimeoutError as error:
            log.error(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def insert_category(cls, doc: CategoryPayload):
        try:
            payload = doc.model_dump_json()
            category_data = json.loads(payload)
            category_data["created_at"] = datetime.utcnow()
            category_data["updated_at"] = datetime.utcnow()
            sanitize(category_data)
            await cls.collection.insert_one(category_data)

        except ServerSelectionTimeoutError as error:
            log.error(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")
