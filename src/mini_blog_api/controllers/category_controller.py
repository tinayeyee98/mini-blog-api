from typing import Any, Dict, List

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query

from ..config import Settings, get_settings
from ..models.base_model import default_responses
from ..models.category_model import Category, CategoryPayload
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
    category_repo: CategoryRepository = Depends(),
    authorization: str = Header(None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    await validate_auth(authorization)

    existing_category = await category_repo.find_category(category.name)

    if existing_category:
        raise HTTPException(status_code=403, detail="Category already exists.")

    await category_repo.insert_category(category)

    raise HTTPException(status_code=201, detail="New category is created.")


@router.get("/cards/category")
async def get_category_list(name: str = Query(None), authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    await validate_auth(authorization)

    query_filter: Dict[str, Any] = {}

    if name is not None:
        query_filter["name"] = name

    docs: List[Category] = await CategoryRepository.find_category_list(
        query_filter=query_filter
    )

    if not docs:
        raise HTTPException(status_code=404, detail="Category not found")

    return docs
