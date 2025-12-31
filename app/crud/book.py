from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, asc
from typing import List, Optional, Dict, Any
from app.models.book import Book, Order
from app.schemas.book import BookCreate, BookUpdate, OrderCreate
from decimal import Decimal
from datetime import date, datetime

class BookCRUD:
    @staticmethod
    def get_book(db: Session, book_id: int):
        return db.query(Book).filter(Book.id == book_id).first()
    
    @staticmethod
    def get_books(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Book).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_books_by_author(db: Session, author: str):
        return db.query(Book).filter(Book.author.ilike(f"%{author}%")).all()
    
    @staticmethod
    def create_book(db: Session, book: BookCreate):
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    
    @staticmethod
    def update_book(db: Session, book_id: int, book_update: BookUpdate):
        db_book = db.query(Book).filter(Book.id == book_id).first()
        if db_book:
            update_data = book_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_book, key, value)
            db.commit()
            db.refresh(db_book)
        return db_book
    
    @staticmethod
    def delete_book(db: Session, book_id: int):
        db_book = db.query(Book).filter(Book.id == book_id).first()
        if db_book:
            db.delete(db_book)
            db.commit()
        return db_book
    
    # SELECT ... WHERE с несколькими условиями
    @staticmethod
    def get_books_by_filters(
        db: Session, 
        genre: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        min_date: Optional[date] = None,
        in_stock: Optional[bool] = None
    ):
        query = db.query(Book)
        
        filters = []
        if genre:
            filters.append(Book.genre == genre)
        if min_price:
            filters.append(Book.price >= min_price)
        if max_price:
            filters.append(Book.price <= max_price)
        if min_date:
            filters.append(Book.published_date >= min_date)
        if in_stock is not None:
            if in_stock:
                filters.append(Book.quantity > 0)
            else:
                filters.append(Book.quantity == 0)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.all()
    
    # JOIN запрос: книги с их заказами
    @staticmethod
    def get_books_with_orders(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Book).join(Order).offset(skip).limit(limit).all()
    
    # GROUP BY: статистика по жанрам
    @staticmethod
    def get_genre_statistics(db: Session):
        return db.query(
            Book.genre,
            func.count(Book.id).label('book_count'),
            func.sum(Book.quantity).label('total_quantity'),
            func.avg(Book.price).label('avg_price')
        ).filter(Book.genre.isnot(None)).group_by(Book.genre).all()
    
    # UPDATE с нетривиальным условием
    @staticmethod
    def apply_discount_to_genre(db: Session, genre: str, discount_percent: Decimal):
        # Применяем скидку ко всем книгам определенного жанра
        return db.query(Book).filter(
            Book.genre == genre,
            Book.price > 0,
            Book.quantity > 0
        ).update(
            {Book.price: Book.price * (1 - discount_percent / 100)},
            synchronize_session=False
        )
    
    # Полнотекстовый поиск по JSON полю
    @staticmethod
    def search_in_metadata(db: Session, search_term: str):
        # Используем PostgreSQL операторы для поиска в JSON
        from sqlalchemy import text
        query = text("""
            SELECT * FROM books 
            WHERE metadata_info::text LIKE :pattern
            OR EXISTS (
                SELECT 1 FROM json_each_text(metadata_info) 
                WHERE value LIKE :pattern
            )
        """)
        return db.execute(query, {"pattern": f"%{search_term}%"}).fetchall()

class OrderCRUD:
    @staticmethod
    def create_order(db: Session, order: OrderCreate):
        # Получаем книгу для расчета цены
        book = db.query(Book).filter(Book.id == order.book_id).first()
        if not book:
            return None
        
        # Проверяем наличие
        if book.quantity < order.quantity:
            return None
        
        # Создаем заказ
        total_price = book.price * order.quantity
        db_order = Order(
            **order.dict(),
            total_price=total_price
        )
        
        # Обновляем количество книг
        book.quantity -= order.quantity
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    
    @staticmethod
    def get_orders_by_customer(db: Session, email: str):
        return db.query(Order).filter(Order.customer_email == email).all()
    
    @staticmethod
    def get_daily_sales(db: Session, target_date: date):
        return db.query(
            func.sum(Order.total_price).label('total_sales'),
            func.count(Order.id).label('order_count')
        ).filter(func.date(Order.order_date) == target_date).first()


    @staticmethod
    def search_books_fulltext(db: Session, search_term: str):
        """Полнотекстовый поиск с использованием pg_trgm"""
        from sqlalchemy import func, or_
        
        # Используем триграммный поиск
        return db.query(Book).filter(
            or_(
                func.similarity(Book.title, search_term) > 0.3,
                func.similarity(Book.author, search_term) > 0.3,
                Book.description.ilike(f"%{search_term}%"),
                Book.metadata_info.cast(sa.Text).ilike(f"%{search_term}%")
            )
        ).order_by(
            func.similarity(Book.title, search_term).desc()
        ).all()