from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import AsyncOpenAI

from app.liteika_api.db.models import FAQEntry
from app.liteika_api.schemas.faq import FAQAnswer
from app.liteika_api.config import config

openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


async def generate_faq_query_embedding(query: str) -> list[float]:
    response = await openai_client.embeddings.create(
        model='text-embedding-3-small',
        input=query
    )
    return response.data[0].embedding


async def get_similar_faq(query: str, session: AsyncSession, limit: int = 5) -> list[FAQAnswer]:
    query_vector = await generate_faq_query_embedding(query)

    stmt = (
        select(FAQEntry)
        .where(FAQEntry.embedding.is_not(None))
        .order_by(FAQEntry.embedding.l2_distance(query_vector))
        .limit(limit)
    )
    result = await session.execute(stmt)
    faqs = result.scalars().all()

    return [FAQAnswer(question=faq.question, answer=faq.answer) for faq in faqs]
