from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from datetime import date

from app.database import get_db
from app.schemas.book import BookCreate, BookUpdate, BookInDB, OrderCreate, OrderInDB
from app.crud.book import BookCRUD, OrderCRUD

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookInDB)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return BookCRUD.create_book(db, book)

@router.get("/", response_model=List[BookInDB])
def read_books(
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = Query(None, description="Поле для сортировки (title, author, price, published_date)"),
    sort_desc: bool = False,
    db: Session = Depends(get_db)
):
    """Получить список книг с пагинацией и сортировкой"""
    from sqlalchemy import asc, desc
    from app.models.book import Book
    
    query = db.query(Book)
    
    # Применяем сортировку
    if sort_by:
        sort_column = getattr(Book, sort_by, None)
        if sort_column:
            query = query.order_by(desc(sort_column) if sort_desc else asc(sort_column))
    
    return query.offset(skip).limit(limit).all()

@router.get("/{book_id}", response_model=BookInDB)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = BookCRUD.get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.put("/{book_id}", response_model=BookInDB)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = BookCRUD.update_book(db, book_id, book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    success = BookCRUD.delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

# Сложные запросы

@router.get("/filter/advanced/")
def get_books_advanced(
    genre: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    min_date: Optional[date] = None,
    in_stock: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """SELECT ... WHERE с несколькими условиями"""
    return BookCRUD.get_books_by_filters(
        db, genre, min_price, max_price, min_date, in_stock
    )

@router.get("/with-orders/")
def get_books_with_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """JOIN запрос: книги с их заказами"""
    return BookCRUD.get_books_with_orders(db, skip, limit)

@router.get("/statistics/genre/")
def get_genre_statistics(db: Session = Depends(get_db)):
    """GROUP BY: статистика по жанрам"""
    return BookCRUD.get_genre_statistics(db)

@router.put("/discount/{genre}/")
def apply_genre_discount(
    genre: str,
    discount_percent: Decimal = Query(..., ge=0, le=100),
    db: Session = Depends(get_db)
):
    """UPDATE с нетривиальным условием: скидка на жанр"""
    updated_count = BookCRUD.apply_discount_to_genre(db, genre, discount_percent)
    db.commit()
    return {"updated_books": updated_count}

@router.get("/search/metadata/")
def search_in_metadata(
    q: str = Query(..., description="Поисковый запрос для JSON поля"),
    db: Session = Depends(get_db)
):
    """Полнотекстовый поиск по JSON полю"""
    results = BookCRUD.search_in_metadata(db, q)
    return [dict(row) for row in results]

# Orders endpoints
@router.post("/orders/", response_model=OrderInDB)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = OrderCRUD.create_order(db, order)
    if db_order is None:
        raise HTTPException(status_code=400, detail="Недостаточно книг на складе или книга не найдена")
    return db_order

@router.get("/orders/daily/{target_date}/")
def get_daily_sales(target_date: date, db: Session = Depends(get_db)):
    sales = OrderCRUD.get_daily_sales(db, target_date)
    return {
        "date": target_date,
        "total_sales": sales.total_sales if sales else 0,
        "order_count": sales.order_count if sales else 0
    }

@router.get("/search/fulltext/")
def search_books_fulltext(
    q: str = Query(..., description="Поисковый запрос для полнотекстового поиска"),
    db: Session = Depends(get_db)
):
    """Полнотекстовый поиск по книгам с использованием pg_trgm"""
    results = BookCRUD.search_books_fulltext(db, q)
    return results