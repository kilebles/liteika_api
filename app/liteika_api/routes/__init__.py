from fastapi import APIRouter

from app.liteika_api.routes import search
from app.liteika_api.routes import compare
from app.liteika_api.routes import faq

router = APIRouter()
     
router.include_router(search.router)
router.include_router(compare.router)
router.include_router(faq.router)