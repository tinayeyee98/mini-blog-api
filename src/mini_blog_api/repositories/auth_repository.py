import json
from datetime import datetime
from typing import Any, Dict

import structlog
from bson.objectid import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

from ..models.auth_model import Auth, AuthPayload
from ..services.auth import generate_pwd, verify_password
from ..services.util import sanitize

log = structlog.get_logger()


class AuthRepository:
    @classmethod
    def initialize(cls, db: AsyncIOMotorClient) -> None:
        cls.collection = db["auth"]

    @classmethod
    async def find_user(cls, username: str):
        try:
            user_dict: Dict[str, Any] = await cls.collection.find_one(
                dict(username=username)
            )

            if user_dict:
                return Auth.model_validate(user_dict)

        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def find_user_by_id(cls, user_id: ObjectId):
        try:
            user_dict: Dict[str, Any] = await cls.collection.find_one(dict(_id=user_id))
            if user_dict:
                return Auth.model_validate(user_dict)

        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def create_user(cls, doc: AuthPayload):
        try:
            payload = doc.model_dump_json()
            author_data = json.loads(payload)
            author_data["password"] = generate_pwd()
            author_data["created_at"] = datetime.utcnow()
            author_data["updated_at"] = datetime.utcnow()
            sanitize(author_data)
            await cls.collection.insert_one(author_data)
            return {
                "username": author_data.get("username"),
                "password": author_data.get("password"),
            }

        except ServerSelectionTimeoutError as error:
            log.msg(error)
            raise HTTPException(500, "Failed to connect to MongoDB.")

    @classmethod
    async def validate_credentials(cls, username: str, password: str):
        user = await cls.find_user(username)

        if not user:
            return None

        if verify_password(password, user.password):
            return user

        return None
