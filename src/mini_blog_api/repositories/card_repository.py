from typing import Any, Dict, List, Optional
from datetime import datetime
from bson.objectid import ObjectId

import json
import structlog
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo.errors import ServerSelectionTimeoutError

from ..models.card_model import Card, CardPayloadCreate
from .author_repository import UserRepository
from ..services.util import sanitize

log = structlog.get_logger()
class CardRepository:
    @classmethod
    def initialize(cls, db: AsyncIOMotorClient) -> None:
        cls.collection = db["cards"]
    
    @classmethod
    async def find_card(cls, card_name: str):
        try:
            card_dict: Dict[str, Any] = await cls.collection.find_one(dict(name=card_name))
            
            if card_dict:
                return Card.model_validate(card_dict)
            
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")
        
    @classmethod
    async def find_card_list(cls, query_filter: Dict[str, Any]) -> List[Card]:
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
    async def update_card(cls, card_name: str, card_data: Dict[str, Any], author: str) -> Optional[Dict]:
        try:
            card = await cls.find_card(card_name)
            
            if not card:
                return None
            
            author_detail = await UserRepository.find_user_by_id(card.author)

            if author_detail.username != author:
                raise HTTPException(status_code=403, detail="You are unauthorized to edit this card")
            
            query = {"name" : card_name}
            set_data = {"$set": card_data}
            
            return await cls.collection.update_one(query, set_data)
            
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")
        
    
    @classmethod
    async def delete_card(cls, card_name: str, author: str):
        try:
           card = await cls.find_card(card_name)
           if not card:
                return None
           
           author_detail = await UserRepository.find_user_by_id(card.author)
           
           if author_detail.username != author:
                raise HTTPException(status_code=403, detail="You are unauthorized to delete this card")
           
           return await cls.collection.delete_one(dict(name=card_name))
            
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")