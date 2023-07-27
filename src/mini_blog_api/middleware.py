from uuid import uuid4
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import MutableHeaders
from starlette_context import context
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import Plugin


class XRequestID(Plugin):
    key = "x-request-id"

    async def extract_value_from_header_by_key(self, request) -> str:
        value = await super().extract_value_from_header_by_key(request)
        if not value:
            value = uuid4()
        return str(value)

    async def enrich_response(self, arg) -> None:
        request_id = str(context.get("x-request-id"))

        # For RawContextMiddleware
        if arg["type"] == "http.response.start":
            headers = MutableHeaders(scope=arg)
            headers.append(self.key, request_id)


class XCorrelationID(Plugin):
    key = "x-correlation-id"

    async def extract_value_from_header_by_key(self, request) -> str:
        value = await super().extract_value_from_header_by_key(request)
        if not value:
            value = uuid4()
        return str(value)

    async def enrich_response(self, arg) -> None:
        correlation_id = str(context.get("x-correlation-id"))

        # For RawContextMiddleware
        if arg["type"] == "http.response.start":
            headers = MutableHeaders(scope=arg)
            headers.append(self.key, correlation_id)


class XForwardedFor(Plugin):
    key = "x-forwarded-for"


class UserAgent(Plugin):
    key = "user-agent"


def cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to HTTP filters."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def context_middleware(app: FastAPI) -> None:
    """Add context middleware to HTTP filters."""
    app.add_middleware(
        RawContextMiddleware,
        plugins=(
            XRequestID(),
            XCorrelationID(),
            XForwardedFor(),
            UserAgent(),
        ),
    )


def configure_middleware(app: FastAPI) -> None:
    """Add available HTTP middleware to HTTP filters."""
    cors_middleware(app)
    context_middleware(app)
