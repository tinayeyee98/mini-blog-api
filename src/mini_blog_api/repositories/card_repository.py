from typing import Any, Dict, List, Optional
from datetime import datetime
from bson.objectid import ObjectId

import structlog
import json
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo.errors import ServerSelectionTimeoutError

from ..models.card_model import Card, CardPayloadCreate
from ..services.util import sanitize

log = structlog.get_logger()
class CardRepository:
    @classmethod
    def initialize(cls, db: AsyncIOMotorClient) -> None:
        cls.collection = db["cards"]
    
    @classmethod
    async def find_card(cls, name):
        try:
            user_dict: Dict[str, Any] = await cls.collection.find_one(dict(name=name))
            if user_dict:
                return Card.model_validate(user_dict)
            
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")
        
    @classmethod
    async def find_category_list(cls, query_filter: Dict[str, Any]) -> List[Card]:
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
    async def insert_card(cls, doc: CardPayloadCreate):
        try:
            card_data = dict(
                name=doc.name,
                status=doc.status,
                category=ObjectId(doc.category),
                author=doc.author,
                content=doc.content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await cls.collection.insert_one(card_data)
     
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")
        
    @classmethod
    async def update_card(cls, card_name: str, card_data: str, author: str) -> Optional[Dict]:
        try:
            card = await cls.find_card(card_name)

            if not card:
                return None
            
            if card.author != author:
                raise HTTPException(status_code=403, detail="You are not authorized to edit this card")
            
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")