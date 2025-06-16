import uvicorn

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.liteika_api.config import config
from app.liteika_api.routes import router as api_router
from app.liteika_api.middlewares.admin_auth import AdminAuthMiddleware
from app.liteika_api.middlewares.cors import setup_cors
from app.liteika_api.admin.templates.admin import setup_admin

app = FastAPI(title='liteika_api')

app.add_middleware(SessionMiddleware, secret_key='super-secret-key')
app.add_middleware(AdminAuthMiddleware)
setup_cors(app)

app.include_router(api_router)
setup_admin(app)

if __name__ == '__main__':
    uvicorn.run(
        'liteika_api.main:app',
        host=config.APP_HOST,
        port=int(config.APP_PORT),
        reload=False
    )
