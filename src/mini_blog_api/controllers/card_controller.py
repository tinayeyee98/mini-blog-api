import structlog
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from bson.objectid import ObjectId

from ..models.base_model import default_responses
from ..models.card_model import Card, CardPayload
from ..repositories.card_repository import CardRepository
from ..repositories.category_repository import CategoryRepository
from ..services.util import sanitize
from ..config import Settings, get_settings

log = structlog.get_logger()
settings: Settings = get_settings()

router = APIRouter(
    tags=["Cards Endpoints"], responses=default_responses,
)


@router.post("/cards", responses=default_responses)
async def create_card(card: CardPayload, card_repo: CardRepository = Depends()):
    existing_card = await card_repo.find_card(card.name)

    if existing_card:
        raise HTTPException(status_code=403, detail="card already exists.")

    category = await CategoryRepository.find_category(card.category)
    
    if category:
        card.category = category.id
    
    await card_repo.insert_card(card)

    resp = dict(
        message="New card is successfully created",
        name=card.name,
        status=card.status,
        category=category.name,
        author=card.author,
        content=card.content,
    )

    raise HTTPException(status_code=201, detail=resp)


@router.get("/cards", responses=default_responses)
async def get_card_list(name: str = Query(None)):
    query_filter: Dict[str, Any] = {}
    
    if name is not None:
        query_filter["name"] = name

    docs: List[Card] = await CardRepository.find_card_list(query_filter=query_filter)

    if not docs:
        raise HTTPException(status_code=404, detail="card not found")

    return docs


# @router.patch("/cards/{card_name:}")
# async def update_card_data(card_name: str, card_data: CardPayload = Depends(), authror: str = Depends()):