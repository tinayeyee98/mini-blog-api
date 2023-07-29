import structlog
import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..models.base_model import default_responses
from ..models.user_model import User, UserPayload
from ..repositories.user_repository import UserRepository
from ..services.auth import create_access_token

from ..config import Settings, get_settings

log = structlog.get_logger()
settings: Settings = get_settings()


router = APIRouter(
    tags=["User Auth Endpoints"], responses=default_responses,
)


@router.post("/auth/register", response_model=User)
async def register_user(user: UserPayload, user_repo: UserRepository = Depends()):
    existing_user = await user_repo.find_user(user.username)

    if existing_user:
        raise HTTPException(status_code=403, detail="Username already exists.")

    user_doc = await user_repo.create_user(user)

    return user_doc


@router.post("/auth/token")
async def access_token_for_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserRepository.validate_credentials(username=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(account=dict(sub=user.username))

    return dict(access_token=access_token, token_type="bearer")
