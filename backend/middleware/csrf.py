import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.core.config import settings

COOKIE_NAME = "access_token"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"

# Endpoints that must NOT be CSRF-protected: they either establish the
# session (no cookie yet), or use a signature-based auth (webhooks).
_CSRF_EXEMPT_PREFIXES = (
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/google",
    "/api/v1/auth/logout",
    "/api/v1/auth/csrf-token",
    "/api/v1/webhooks",
    "/api/v1/billing/webhook",
)

_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method.upper()

        # Only protect cookie-authenticated, state-changing requests.
        is_mutating = method in _MUTATING_METHODS
        has_cookie_auth = COOKIE_NAME in request.cookies
        is_exempt = path.startswith(_CSRF_EXEMPT_PREFIXES)

        if is_mutating and has_cookie_auth and not is_exempt:
            header_token = request.headers.get(CSRF_HEADER)
            cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

            if not header_token or not cookie_token or not secrets.compare_digest(header_token, cookie_token):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token mismatch. Refresh the page and try again."},
                )

        response = await call_next(request)
        return response
