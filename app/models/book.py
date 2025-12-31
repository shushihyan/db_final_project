from sqlalchemy import Column, Integer, String, Text, Date, JSON, ForeignKey, Index, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    isbn = Column(String(13), unique=True, index=True)
    published_date = Column(Date, index=True)
    genre = Column(String(50), index=True)
    price = Column(Numeric(10, 2), index=True)
    quantity = Column(Integer, default=0)
    description = Column(Text)
    
    # JSON поле для дополнительных метаданных
    metadata_info = Column(JSONB, nullable=True, default=dict)
    
    # Связь с заказами
    orders = relationship("Order", back_populates="book")
    
    # GIN индекс для полнотекстового поиска по JSON полю
    __table_args__ = (
        Index('ix_books_metadata_info_gin', metadata_info, postgresql_using='gin'),
    )

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False, index=True)
    order_date = Column(Date, nullable=False, index=True)
    quantity = Column(Integer, default=1)
    total_price = Column(Numeric(10, 2))
    status = Column(String(20), default="pending", index=True)
    
    # Связи
    book = relationship("Book", back_populates="orders")

# Модель для статистики
class BookStat(Base):
    __tablename__ = "book_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), unique=True)
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Numeric(10, 2), default=0)
    average_rating = Column(Numeric(3, 2))
    
    book = relationship("Book")