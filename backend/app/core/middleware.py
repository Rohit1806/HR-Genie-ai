from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import uuid
import time
import logging

logger = logging.getLogger(__name__)

# State-changing methods that should be audit logged
AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Paths to skip audit logging
SKIP_AUDIT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/api/v1/auth/refresh"}


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log all state-changing requests with timing."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Only log state-changing requests
        if (
            request.method in AUDIT_METHODS
            and request.url.path not in SKIP_AUDIT_PATHS
        ):
            user_id = getattr(request.state, "user_id", "anonymous")
            logger.info(
                "audit_log",
                extra={
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "user_id": user_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "ip": request.client.host if request.client else "unknown",
                }
            )

        return response
