from typing import Any, ClassVar, Dict, List, Optional

import structlog
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import ServerSelectionTimeoutError

from ..models.user import User
from ..repositories.db import MongoMotorCollection

log = structlog.get_logger()


class UserRepository(MongoMotorCollection):
    __collection_name__: ClassVar[str] = "users"
    __db_collection__: ClassVar[AsyncIOMotorCollection] = None

    @classmethod
    def initialize(cls, db):
        cls.__db_collection__ = db[cls.__collection_name__]

    @classmethod
    async def find_one(cls, projection: Optional[Dict[str, Any]] = None, **kwargs):
        try:
            doc: Dict[str, Any] = await cls.__db_collection__.find_one(
                kwargs, projection=projection
            )
            if doc:
                return User.model_validate(doc)
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")
    
    # @classmethod
    # async def insert_one(
    #     cls, query: str, entry: str
    # ) -> Optional[User]:
    #     try:
