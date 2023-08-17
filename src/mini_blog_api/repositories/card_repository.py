from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from bson.objectid import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo.errors import ServerSelectionTimeoutError

from ..models.card_model import Card, CardPayloadCreate
from .auth_repository import AuthRepository

log = structlog.get_logger()


class CardRepository:
    @classmethod
    def initialize(cls, db: AsyncIOMotorClient) -> None:
        cls.collection = db["cards"]

    @classmethod
    async def find_one(cls, **kwargs) -> Optional[Card]:
        try:
            card_dict: Dict[str, Any] = await cls.collection.find_one(kwargs)
            if card_dict:
                return Card.model_validate(card_dict)

        except ServerSelectionTimeoutError as error:
            log.error(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def find(cls, query_filter: Dict[str, Any]) -> List[Card]:
        try:
            docs: List[Card] = []
            db_cursor: AsyncIOMotorCursor = cls.collection.find(query_filter)
            async for doc in db_cursor:
                docs.append(Card.model_validate(doc))
            return docs

        except ServerSelectionTimeoutError as error:
            log.error(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def find(
        cls,
        query_filter: Dict[str, Any],
        skip: int,
        limit: int,
        projection: Optional[Dict[str, Any]] = None,
    ):
        try:
            docs: List[Card] = []
            db_cursor: AsyncIOMotorCursor = cls.collection.find(
                query_filter, projection, skip, limit
            )
            async for doc in db_cursor:
                docs.append(Card.model_validate(doc))
            return docs

        except ServerSelectionTimeoutError as error:
            log.error(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def insert_one(cls, doc: CardPayloadCreate, current_user: str):
        try:
            card_data = dict(
                name=doc.name,
                status=doc.status,
                category=ObjectId(doc.category),
                author=ObjectId(current_user),
                content=doc.content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            inserted_data = await cls.collection.insert_one(card_data)
            return inserted_data.inserted_id

        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def update_one(
        cls, card_id: str, card_data: Dict[str, Any], current_user: str
    ) -> Optional[Dict]:
        try:
            card = await CardRepository.find_one(**dict(_id=ObjectId(card_id)))

            if not card:
                return None

            card_author = await AuthRepository.find_one(
                **dict(_id=ObjectId(card.author))
            )

            if not card_author:
                return None

            if ObjectId(card_author.id) != ObjectId(current_user):
                raise HTTPException(
                    status_code=403, detail="You are unauthorized to edit this card"
                )

            query = {"_id": ObjectId(card_id)}
            set_data = {"$set": card_data}

            return await cls.collection.update_one(query, set_data)

        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def delete_one(cls, card_id: str, current_user: str):
        try:
            card = await CardRepository.find_one(**dict(_id=ObjectId(card_id)))

            if not card:
                return None

            card_author = await AuthRepository.find_one(
                **dict(_id=ObjectId(card.author))
            )

            if not card_author:
                return None

            if ObjectId(card_author.id) != ObjectId(current_user):
                raise HTTPException(
                    status_code=403, detail="You are unauthorized to edit this card"
                )

            return await cls.collection.delete_one(dict(_id=ObjectId(card_id)))

        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")
