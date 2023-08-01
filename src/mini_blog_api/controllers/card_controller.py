from typing import Any, Dict, List

import structlog
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request

from ..config import Settings, get_settings
from ..models.base_model import default_responses
from ..models.card_model import Card, CardPayload, CardQueryParams
from ..repositories.card_repository import CardRepository
from ..repositories.category_repository import CategoryRepository

log = structlog.get_logger()
settings: Settings = get_settings()


router = APIRouter(
    tags=["Cards Endpoints"],
    responses=default_responses,
)


@router.post("/cards", responses=default_responses)
async def create_card(
    request: Request,
    card: CardPayload,
):
    existing_card = await CardRepository.find_one(**dict(name=card.name))

    if existing_card:
        raise HTTPException(status_code=403, detail="card already exists.")

    category = await CategoryRepository.find_one(**dict(_id=ObjectId(card.category)))

    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")

    inserted_result = await CardRepository.insert_one(card, request.state.user)

    resp = dict(
        message="New card is successfully created.", card_id=str(inserted_result)
    )

    raise HTTPException(status_code=201, detail=resp)


@router.get("/cards/{card_id}", response_model=Card)
async def get_card_by_id(card_id: str):
    card_dict: Card = await CardRepository.find_one(**dict(_id=ObjectId(card_id)))
    if card_dict:
        return card_dict
    else:
        raise HTTPException(status_code=404, detail="Category not found")


@router.get("/cards", responses=default_responses)
async def get_card_list(query_params: CardQueryParams = Depends()):
    query_filter: Dict[str, Any] = {}

    if query_params.id:
        query_filter["_id"] = ObjectId(query_params.id)

    if query_params.name:
        query_filter["name"] = query_params.name

    docs: List[Card] = await CardRepository.find(
        query_filter=query_filter, skip=query_params.skip, limit=query_params.limit
    )

    if not docs:
        raise HTTPException(status_code=404, detail="Cards not found")

    return {"cards": docs}


@router.patch("/cards/{card_id}")
async def update_card_data(
    card_id: str,
    request: Request,
):
    payload = await request.json()
    updated_card = await CardRepository.update_one(card_id, payload, request.state.user)

    if not updated_card:
        raise HTTPException(status_code=404, detail="Card not found")

    raise HTTPException(status_code=200, detail="Card is updated.")


@router.delete("/cards/{card_id}", responses=default_responses)
async def delete_card_by_name(
    request: Request,
    card_id: str,
):
    deleted_card = await CardRepository.delete_one(card_id, request.state.user)

    if not deleted_card:
        raise HTTPException(status_code=404, detail="Card not found.")

    raise HTTPException(status_code=204, detail="Card is deleted.")
