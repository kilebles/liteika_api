from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView, action
from starlette.responses import RedirectResponse
from starlette.requests import Request

from app.liteika_api.config import config
from app.liteika_api.db.models import FAQEntry
from app.liteika_api.utils.generate_faq_embeddings import generate_embedding_for_text

SYNC_DATABASE_URL = config.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql')
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)


def setup_admin(app):
    admin = Admin(app, sync_engine, templates_dir='app/liteika_api/admin/templates')

    class FAQEntryAdmin(ModelView, model=FAQEntry):
        column_list = [FAQEntry.id, FAQEntry.question, FAQEntry.answer]
        form_columns = ['question', 'answer']

        @action(
            name='regenerate_embeddings',
            label='Перегенерировать эмбеддинги'
        )
        async def regenerate_embeddings(self, request: Request):
            pks_param = request.query_params.get('pks')
            if not pks_param:
                print("Нет выбранных записей для обновления эмбеддингов.")
                return RedirectResponse(request.url_for("admin:list", identity=self.identity))

            pk_list = [int(pk) for pk in pks_param.split(',') if pk.strip().isdigit()]
            print(f"Выбрано записей: {pk_list}")

            with Session(bind=sync_engine) as session:
                entries = session.scalars(
                    select(FAQEntry).where(FAQEntry.id.in_(pk_list))
                ).all()

                updated_count = 0

                for entry in entries:
                    text = f'{entry.question.strip()}\n{entry.answer.strip()}'
                    try:
                        response = await generate_embedding_for_text(text)
                        entry.embedding = response
                        print(f"OK → ID {entry.id}")
                        updated_count += 1
                    except Exception as e:
                        print(f"Ошибка при генерации эмбеддинга для ID {entry.id}: {e}")

                session.commit()

            request.session['admin_flash'] = f"Успешно обновлено {updated_count} записей."
            return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    admin.add_view(FAQEntryAdmin)
