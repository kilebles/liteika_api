from fastapi import APIRouter

from app.liteika_api.routes import faq

router = APIRouter()
     
router.include_router(faq.router)