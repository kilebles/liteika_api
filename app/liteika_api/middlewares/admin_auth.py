import base64

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.liteika_api.config import config


class AdminAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith('/admin'):
            auth = request.headers.get('Authorization')
            expected = 'Basic ' + base64.b64encode(f'{config.ADMIN_USERNAME}:{config.ADMIN_PASSWORD}'.encode()).decode()
            if auth != expected:
                return Response(status_code=401, headers={'WWW-Authenticate': 'Basic'}, content='Unauthorized')
        return await call_next(request)
