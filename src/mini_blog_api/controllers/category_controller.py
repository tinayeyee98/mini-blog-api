import structlog
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query

from ..models.base_model import default_responses
from ..models.category_model import Category, CategoryPayload
from ..repositories.category_repository import CategoryRepository
from ..services.util import sanitize
from ..config import Settings, get_settings

log = structlog.get_logger()
settings: Settings = get_settings()

router = APIRouter(
    tags=["Card's Category Endpoints"], responses=default_responses,
)


@router.post("/cards/category")
async def create_category(category: CategoryPayload, category_repo: CategoryRepository = Depends()):
    existing_category = await category_repo.find_category(category.name)

    if existing_category:
        raise HTTPException(status_code=403, detail="Category already exists.")

    await category_repo.insert_category(category)

    raise HTTPException(status_code=201, detail="New category is created.")


@router.get("/cards/category")
async def get_category_list(name: str = Query(None)):
    query_filter: Dict[str, Any] = {}
    
    if name is not None:
        query_filter["name"] = name

    docs: List[Category] = await CategoryRepository.find_category_list(query_filter=query_filter)

    if not docs:
        raise HTTPException(status_code=404, detail="Category not found")

    return docs

