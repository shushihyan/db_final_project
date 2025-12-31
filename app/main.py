from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.database import engine, Base
from app import models  # ensure model modules are imported so SQLAlchemy registers them
from app.routers import books

# Создаем таблицы в базе данных
# Use Base from `app.database` (models package doesn't export Base).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management API",
    description="REST API для управления библиотекой книг",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(books.router)

@app.get("/")
def read_root():
    return {
        "message": "Добро пожаловать в Library Management API!",
        "docs": "/docs",
        "endpoints": {
            "books": "/books/",
            "books_with_orders": "/books/with-orders/",
            "genre_statistics": "/books/statistics/genre/",
            "metadata_search": "/books/search/metadata/?q=search_term",
            "daily_sales": "/books/orders/daily/{date}/"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Library Management API"}