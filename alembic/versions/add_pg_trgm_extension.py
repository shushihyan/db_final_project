"""add pg_trgm extension for full-text search

Revision ID: add_pg_trgm_extension
Revises: 59c5a1aef1d2
Create Date: 2025-12-31 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_pg_trgm_extension'
down_revision = '59c5a1aef1d2'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Добавляем расширение pg_trgm для полнотекстового поиска
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
    # Создаем триграммный индекс для поля title
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_books_title_trgm 
        ON books 
        USING gin (title gin_trgm_ops);
    """)
    
    # Создаем триграммный индекс для поля author
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_books_author_trgm 
        ON books 
        USING gin (author gin_trgm_ops);
    """)

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_books_author_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_books_title_trgm;")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
