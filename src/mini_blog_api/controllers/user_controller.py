import structlog
import jwt
from fastapi import APIRouter, Depends, HTTPException

from ..models.base_model import default_responses
from ..models.user_model import User
from ..repositories.db import UsersCollection
from ..config import Settings, get_settings

log = structlog.get_logger()
settings: Settings = get_settings()


openapi_tags = [
    {
        "name" : "User Auth",
        "description": "Endpoints for user auth controller",
    }
]

router = APIRouter(
    tags=["auth"], responses=default_responses,
)

def generate_token(user: User) -> str:
    token = jwt.encode(user.model_dump(), settings.jwt_secret, algorithm=settings.jwt_alg)


@router.post("/register/", response_model=None)
async def register_user(user: User, user_repo: UsersCollection = Depends()) -> dict:
    existing_user = await user_repo.find_one(user.username)
    
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    await user_repo.insert_one(user)


