import uuid
from contextvars import ContextVar
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that runs on every request:
    - Generates a unique request_id
    - Binds request_id, tenant_id, user_id, org_role to all logs
    - Adds X-Request-ID to response headers
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        # tenant_id/user_id are not available yet — JWT verification happens inside the route handler
        logger.info("request_started")
        response = await call_next(request)

        # Re-bind with tenant context now that the route handler has run and set request.state
        structlog.contextvars.bind_contextvars(
            tenant_id=getattr(request.state, "tenant_id", "anonymous"),
            user_id=getattr(request.state, "user_id", "anonymous"),
            org_role=getattr(request.state, "org_role", "anonymous"),
        )

        logger.info("request_completed", status_code=response.status_code)
        response.headers["X-Request-ID"] = request_id
        return response