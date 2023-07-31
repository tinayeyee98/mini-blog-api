import base64
import binascii
from uuid import uuid4

import httpx
import jwt
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidSignatureError,
    InvalidTokenError,
    MissingRequiredClaimError,
)
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.datastructures import MutableHeaders
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette_context import context
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import Plugin

from .config import Settings, get_settings
from .services import util

log = structlog.get_logger()
settings: Settings = get_settings()


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


class AuthException(AuthenticationError):
    def __init__(self, message, status_code=403):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def auth_bearer(token):
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
        return claims
    except InvalidAlgorithmError:
        raise HTTPException(status_code=403, detail="Unsupported algorithm in token")
    except InvalidSignatureError:
        raise HTTPException(status_code=403, detail="Invalid signature error")
    except MissingRequiredClaimError as exc:
        raise HTTPException(status_code=403, detail=f"Essential claims missing. {exc}")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"{exc}")


def auth_basic(credentials):
    try:
        decoded = base64.b64decode(credentials).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error):
        raise AuthenticationError("Invalid auth credentials")

    client_id, _, client_secret = decoded.partition(":")

    headers = {
        "content-type": "application/json",
    }

    try:
        with httpx.Client(headers=headers) as httpclient:
            result = httpclient.get(
                settings.generate_apikey_url + f"?username={client_id}"
            )
            result.raise_for_status()
    except (httpx.RequestError, httpx.ConnectError):
        raise AuthException(
            "Authorization verification is temporarily unavailable", 503
        )
    except httpx.HTTPStatusError:
        raise AuthException("Authorization failed", 403)

    apikey = result.json()

    secret = apikey.get("client_secret", None)
    if secret != client_secret:
        raise AuthException("Invalid API Key", 403)

    claims = dict(sub=client_id)
    return claims


class TokenAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        if not request.get("Authorization"):
            return

        auth_header = request.get("Authorization")
        scheme, auth = auth_header.split()
        scheme = scheme.lower()

        if scheme == "bearer":
            claims = auth_bearer(auth)
        elif scheme == "basic":
            claims = auth_basic(auth)
        else:
            raise AuthException("Unsupported authorization scheme", 400)

        return AuthCredentials(["authenticated"]), SimpleUser(claims.get("sub", ""))


def cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to HTTP filters."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


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


def auth_middleware(app: FastAPI) -> None:
    app.add_middleware(AuthenticationMiddleware, backend=TokenAuthBackend())


def configure_middleware(app: FastAPI) -> None:
    """Add available HTTP middleware to HTTP filters."""
    cors_middleware(app)
    context_middleware(app)
    auth_middleware(app)
