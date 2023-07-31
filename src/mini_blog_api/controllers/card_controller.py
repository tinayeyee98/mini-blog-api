import structlog
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, Header, Request

from ..models.base_model import default_responses
from ..models.card_model import Card, CardPayload
from ..repositories.card_repository import CardRepository
from ..repositories.category_repository import CategoryRepository
from ..repositories.author_repository import UserRepository
from ..services.auth import get_current_user, validate_auth
from ..config import Settings, get_settings

log = structlog.get_logger()
settings: Settings = get_settings()

router = APIRouter(
    tags=["Cards Endpoints"], responses=default_responses,
)


@router.post("/cards", responses=default_responses)
async def create_card(card: CardPayload, card_repo: CardRepository = Depends(), authorization: str = Header(None)):
            
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    
    await validate_auth(authorization)

    existing_card = await card_repo.find_card(card.name)

    if existing_card:
        raise HTTPException(status_code=403, detail="card already exists.")

    category = await CategoryRepository.find_category(card.category)
    author = await UserRepository.find_user(card.author)

    if not author:
        raise HTTPException(status_code=404, detail="Author not found.")
    elif not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    
    if category:
        card.category = category.id
    
    if author:
        card.author = author.id

    await card_repo.insert_card(card)

    resp = dict(
        message="New card is successfully created",
        name=card.name,
        status=card.status,
        category=category.name,
        author=author.username,
        content=card.content,
    )

    raise HTTPException(status_code=201, detail=resp)


@router.get("/cards", responses=default_responses)
async def get_card_list(name: str = Query(None), authorization: str = Header(None)):
            
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    
    await validate_auth(authorization)

    query_filter: Dict[str, Any] = {}
    
    if name is not None:
        query_filter["name"] = name

    docs: List[Card] = await CardRepository.find_card_list(query_filter=query_filter)

    if not docs:
        raise HTTPException(status_code=404, detail="card not found")

    return docs


@router.patch("/cards/{card_name}")
async def update_card_data(card_name: str, card_data: Request, authorization: str = Header(None), current_user: str = Depends(get_current_user)):
                
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    
    await validate_auth(authorization)
    
    payload = await card_data.json()
    updated_card = await CardRepository.update_card(card_name, payload, current_user)

    if not updated_card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    raise HTTPException(status_code=200, detail="Card is updated.")


@router.delete("/cards/{card_name}", responses=default_responses)
async def delete_card_by_name(card_name: str, authorization: str = Header(None), current_user: str = Depends(get_current_user)):
                    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    
    await validate_auth(authorization)

    deleted_card = await CardRepository.delete_card(card_name, current_user)

    if not deleted_card:
        raise HTTPException(status_code=404, detail="Card not found.")
    
    raise HTTPException(status_code=204, detail="Card is deleted.")