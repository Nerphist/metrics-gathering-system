import os

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from auth_api import auth_user

SERVER_API_KEY = os.environ.get('SERVER_API_KEY', '123')


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        headers = dict(request.headers)

        if headers.get('Server-Api-Key') == SERVER_API_KEY:
            return await call_next(request)

        if auth_user(headers):
            return await call_next(request)

        return JSONResponse(content={'detail': 'Authorization Error'}, status_code=401)
