from typing import Any, Dict
from datetime import datetime

import structlog
import json
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

from ..models.user_model import User, UserPayload
from ..services.util import sanitize
from ..services.auth import generate_pwd, verify_password

log = structlog.get_logger()
class UserRepository:
    @classmethod
    def initialize(cls, db: AsyncIOMotorClient) -> None:
        cls.collection = db["users"]

    async def find_user(cls, username):
        try:
            user_dict: Dict[str, Any] = await cls.collection.find_one(dict(username=username))
            if user_dict:
                return User.model_validate(user_dict)
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")
    
    @classmethod
    async def create_user(cls, doc: UserPayload):
        try:
            payload = doc.model_dump_json()
            user_data = json.loads(payload)
            user_data["password"] = generate_pwd()
            user_data["created_at"] = datetime.utcnow()
            user_data["updated_at"] = datetime.utcnow()
            sanitize(user_data)
            await cls.collection.insert_one(user_data)
            return {"username": user_data.get("username"), "password": user_data.get("password")}
        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.") 
    
    @classmethod
    async def validate_credentials(cls, username: str, password: str):
        user = await cls.find_user(cls, username)

        if not user:
            return None
        
        if verify_password(password, user.password):
            return user
        
        return None
