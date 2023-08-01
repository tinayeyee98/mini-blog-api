from typing import Any, Dict, List

import structlog
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Header, HTTPException, Query

from ..config import Settings, get_settings
from ..models.base_model import default_responses
from ..models.category_model import Category, CategoryPayload, CategoryQueryParams
from ..repositories.category_repository import CategoryRepository
from ..services.auth import validate_auth

log = structlog.get_logger()
settings: Settings = get_settings()


router = APIRouter(
    tags=["Card's Category Endpoints"],
    responses=default_responses,
)


@router.post("/cards/category")
async def create_category(
    category: CategoryPayload,
    authorization: str = Header(None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    await validate_auth(authorization)

    existing_category = await CategoryRepository.find_one(**dict(name=category.name))

    if existing_category:
        raise HTTPException(status_code=403, detail="Category already exists.")

    await CategoryRepository.insert_one(category)

    raise HTTPException(status_code=201, detail="New category is created.")


@router.get("/cards/category/{category_id}", response_model=Category)
async def get_site_by_site_code(category_id: str, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    await validate_auth(authorization)
    category_dict: Category = await CategoryRepository.find_one(
        **dict(_id=ObjectId(category_id))
    )
    if category_dict:
        return category_dict
    else:
        raise HTTPException(status_code=404, detail="Category not found")


@router.get("/cards/category")
async def get_category_list(
    query_params: CategoryQueryParams = Depends(), authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    await validate_auth(authorization)

    query_filter: Dict[str, Any] = {}

    if query_params.id:
        query_filter["_id"] = ObjectId(query_params.id)

    if query_params.name:
        query_filter["name"] = query_params.name

    docs: List[Category] = await CategoryRepository.find(
        query_filter=query_filter, skip=query_params.skip, limit=query_params.limit
    )

    if not docs:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"category": docs}
