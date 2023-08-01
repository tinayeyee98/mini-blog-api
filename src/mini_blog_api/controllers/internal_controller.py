import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from starlette_context import context

from ..config import Settings, get_settings
from ..models.base_model import AppInfo, default_responses

log = structlog.get_logger()

openapi_tags = [
    {
        "name": "internal",
        "description": "Endpoints for internal operations such as active healthchecking from control-plane.",
    }
]

router = APIRouter(tags=["internal"], responses=default_responses)


@router.get("/app_info", response_model=AppInfo)
async def app_info(request: Request, settings: Settings = Depends(get_settings)):
    log.msg("app info retrieved", **context.data)
    return request.app.info


@router.get(
    "/healthcheck",
    response_class=PlainTextResponse,
    responses={200: {"content": {"text/plain": {"example": "T0sK"}}}},
)
async def healthcheck(settings: Settings = Depends(get_settings)):
    log.msg(
        "healthcheck responded",
        status_code=200,
        response_content=settings.healthcheck_response,
        **context.data,
    )
    return PlainTextResponse(settings.healthcheck_response)


@router.get("/testing")
async def testing():
    return PlainTextResponse("Hello World!")
