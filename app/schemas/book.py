from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Dict, Any
from decimal import Decimal

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=10, max_length=13)
    published_date: Optional[date] = None
    genre: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    quantity: Optional[int] = Field(0, ge=0)
    description: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

class BookInDB(BookBase):
    id: int
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    book_id: int
    customer_name: str
    # Use plain str for email to avoid the optional dependency on `email-validator`.
    # If you later want stricter validation, install `email-validator` and switch
    # this back to `EmailStr`.
    customer_email: str = Field(..., min_length=3, max_length=320)
    order_date: date
    quantity: int = Field(1, ge=1)
    status: Optional[str] = "pending"

class OrderCreate(OrderBase):
    pass

class OrderInDB(OrderBase):
    id: int
    total_price: Decimal
    
    class Config:
        from_attributes = True