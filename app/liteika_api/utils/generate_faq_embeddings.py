import asyncio
import logging

from sqlalchemy import select
from openai import AsyncOpenAI

from app.liteika_api.db.session import async_session_maker
from app.liteika_api.db.models import FAQEntry
from app.liteika_api.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

MODEL_NAME = 'text-embedding-3-small'
BATCH_SIZE = 100


async def generate_faq_embeddings():
    async with async_session_maker() as session:
        # Просто забираем все записи, без фильтра по embedding
        result = await session.execute(select(FAQEntry))
        records = result.scalars().all()

        if not records:
            logger.info("В таблице FAQ нет записей.")
            return

        logger.info(f"Всего записей FAQ: {len(records)}. Начинаем генерацию эмбеддингов...")

        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i + BATCH_SIZE]
            texts = [
                f'{entry.question.strip()}\n{entry.answer.strip()}'
                for entry in batch
            ]

            try:
                response = await client.embeddings.create(
                    input=texts,
                    model=MODEL_NAME,
                    encoding_format="float"
                )
                for record, item in zip(batch, response.data):
                    record.embedding = item.embedding

                logger.info(f"Обработано {len(batch)} записей (ID: {batch[0].id} – {batch[-1].id})")
            except Exception as e:
                logger.error(f"Ошибка при генерации эмбеддингов (ID {batch[0].id}): {e}")

        await session.commit()
        logger.info("Эмбеддинги FAQ успешно сгенерированы и сохранены.")
        
        
async def generate_embedding_for_text(text: str) -> list[float]:
    response = await client.embeddings.create(
        input=[text],
        model=MODEL_NAME,
        encoding_format="float"
    )
    return response.data[0].embedding


def generate_embedding_for_text_sync(text: str) -> list[float]:
    """Sync wrapper for generate_embedding_for_text"""
    return asyncio.run(generate_embedding_for_text(text))


if __name__ == '__main__':
    asyncio.run(generate_faq_embeddings())
