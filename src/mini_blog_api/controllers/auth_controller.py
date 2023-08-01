import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..config import Settings, get_settings
from ..models.auth_model import UserAuthPayload
from ..models.base_model import default_responses
from ..repositories.auth_repository import AuthRepository
from ..services.auth import generate_access_token

log = structlog.get_logger()
settings: Settings = get_settings()

router = APIRouter(
    tags=["UserAuth Endpoints"],
    responses=default_responses,
)


@router.post("/auth/register", responses=default_responses)
async def register_user(user: UserAuthPayload):
    existing_user = await AuthRepository.find_one(**dict(name=user.username))

    if existing_user:
        raise HTTPException(status_code=403, detail="Username already exists.")

    user_doc = await AuthRepository.insert_one(user)

    return user_doc


@router.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await AuthRepository.validate_credentials(
        username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = generate_access_token(account=dict(sub=str(user.id)))

    return dict(access_token=access_token, token_type="bearer")
