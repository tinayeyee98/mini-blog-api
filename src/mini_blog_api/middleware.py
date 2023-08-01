import typing

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidSignatureError,
    MissingRequiredClaimError,
)
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from .config import Settings, get_settings
from .services.util import strtolist

settings: Settings = get_settings()

routes_to_protect = strtolist(settings.routes_to_exclude)


class Authorization(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        path = request.url.path

        if path in routes_to_protect:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=403, content={"reason": "Authorization token is missing"}
            )

        scheme, token = auth_header.split()
        scheme = scheme.lower()

        try:
            claims = jwt.decode(
                token, settings.jwt_secret, algorithms=[settings.jwt_alg]
            )
            user = claims.get("sub")
            if user is None:
                return HTTPException(status_code=401, detail="Invalid token.")

            request.state.user = user

            return await call_next(request)
        except InvalidAlgorithmError:
            return JSONResponse(
                status_code=403, content={"reason": "Unsupported algorithm in token"}
            )
        except InvalidSignatureError:
            return JSONResponse(
                status_code=403, content={"reason": "Invalid signature error"}
            )
        except MissingRequiredClaimError as exc:
            return JSONResponse(status_code=403, content={"reason": str(exc)})
        except ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"reason": "Expired"})
        except jwt.PyJWTError as exc:
            return JSONResponse(status_code=401, content={"reason": str(exc)})
