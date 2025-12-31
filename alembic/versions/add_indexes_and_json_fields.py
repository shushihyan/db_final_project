# Создаем файл миграции вручную: alembic/versions/add_json_field_and_indexes.py
"""
Добавление JSON поля и индексов для полнотекстового поиска
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_json_field_and_indexes'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Добавляем JSON поле
    op.add_column('books', sa.Column('metadata_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Добавляем GIN индекс для JSON поля
    op.execute("""
        CREATE INDEX ix_books_metadata_info_gin ON books 
        USING gin (metadata_info);
    """)
    
    # Добавляем pg_trgm расширение для полнотекстового поиска
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    
    # Создаем индекс для поиска по названию с использованием pg_trgm
    op.execute("""
        CREATE INDEX ix_books_title_trgm ON books 
        USING gin (title gin_trgm_ops);
    """)
    
    # Создаем таблицу статистики
    op.create_table('book_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=True),
        sa.Column('total_orders', sa.Integer(), nullable=True),
        sa.Column('total_revenue', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('average_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_book_stats_book_id'), 'book_stats', ['book_id'], unique=True)
    op.create_index(op.f('ix_book_stats_id'), 'book_stats', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_book_stats_id'), table_name='book_stats')
    op.drop_index(op.f('ix_book_stats_book_id'), table_name='book_stats')
    op.drop_table('book_stats')
    op.drop_index('ix_books_title_trgm', table_name='books')
    op.drop_index('ix_books_metadata_info_gin', table_name='books')
    op.drop_column('books', 'metadata_info')
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")