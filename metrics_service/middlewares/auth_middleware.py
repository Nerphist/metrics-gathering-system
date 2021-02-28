from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from auth_api import auth_user


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not auth_user(dict(request.headers)):
            response = JSONResponse(content={'details': 'Authorization Error'})
        else:
            response = await call_next(request)
        return response
