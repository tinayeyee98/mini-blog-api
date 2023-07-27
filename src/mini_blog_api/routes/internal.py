import structlog
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from starlette_context import context

log = structlog.get_logger()

openapi_tags = [
    {
        "name" : "internal",
        "description": "Endpoints for internal operations such as active healthchecking from control-plane.",
    }
]

router = APIRouter(
    tags=["internal"],
)

@router.get("/app_info", response_class=PlainTextResponse)
async def server_info(request: Request):
    log.msg("app info provided", **context.data)
    return PlainTextResponse(f"{request.app.title}/{request.app.version}", 200)


@router.get("/healthcheck", response_class=PlainTextResponse)
async def healthcheck():
    log.msg("healthcheck responded", **context.data)
    return PlainTextResponse("OK", 200)
