from abc import ABC, abstractclassmethod
from typing import Any, ClassVar, Dict, List, Optional

import structlog
from fastapi import HTTPException
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pymongo.errors import ServerSelectionTimeoutError
from ..models.user_model import User

log = structlog.get_logger()


def get_db(db_uri: str, db_name: str) -> AsyncIOMotorDatabase:
    """Get asyncio database connection."""
    try:
        dbc: AsyncIOMotorClient = AsyncIOMotorClient(
            db_uri, serverSelectionTimeoutMS=10)
        return dbc.get_database(db_name)

    except ServerSelectionTimeoutError as error:
        log.msg(error)
        raise HTTPException(500, "Failed to connect to MongoDB.")


class MongoMotorCollection(ABC):
    @abstractclassmethod
    def initialize(cls, db: AsyncIOMotorDatabase) -> None:
        pass

    @abstractclassmethod
    async def find_one(cls, *args: Any, **kwargs: Any) -> Any:
        pass

class UsersCollection(MongoMotorCollection):
    __collection_name__: ClassVar[str] = "users"
    __db_collection__: ClassVar[AsyncIOMotorCollection] = None

    @classmethod
    def initialize(cls, db: AsyncIOMotorClient):
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
    
    @classmethod
    async def insert_one(cls, doc: User) -> None:
        try:
            payload = doc.model_dump_json()
            log.msg(payload)

        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.") 
