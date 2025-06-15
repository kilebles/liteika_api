from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.liteika_api.db.session import get_async_session
from app.liteika_api.schemas.faq import FAQQuery, FAQAnswer
from app.liteika_api.services.faq_service import get_similar_faq

router = APIRouter()


@router.post('/faq/search')
async def faq_search(
    body: FAQQuery,
    session: AsyncSession = Depends(get_async_session),
):
    faqs = await get_similar_faq(body.query, session)
    
    return {
        'query': body.query,
        'result': [
            {
                'question': faq.question,
                'answer': faq.answer
            }
            for faq in faqs
        ]
    }