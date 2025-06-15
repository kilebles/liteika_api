import csv
import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.liteika_api.db.models import FAQEntry
from app.liteika_api.db.session import async_session_maker

CSV_PATH = Path('faq.csv')


def clean_text(text: str) -> str | None:
    if text is None:
        return None
    value_str = str(text).strip()
    return value_str if value_str and value_str.lower() != 'nan' else None


async def import_faq():
    async with async_session_maker() as session:
        with CSV_PATH.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                question = clean_text(row.get('question'))
                answer = clean_text(row.get('answer'))

                if not question or not answer:
                    continue

                result = await session.execute(
                    select(FAQEntry).where(FAQEntry.question == question)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    print(f'Updating answer for: {question}')
                    existing.answer = answer
                else:
                    faq = FAQEntry(question=question, answer=answer)
                    session.add(faq)
                    print(f'Added new FAQ: {question}')

        await session.commit()


if __name__ == '__main__':
    asyncio.run(import_faq())
