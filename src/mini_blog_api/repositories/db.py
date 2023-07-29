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
from ..models.user_model import UserPayload, User

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
