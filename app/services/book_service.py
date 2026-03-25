from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


async def create_book(db: AsyncSession, data: BookCreate) -> Book:
    book = Book(**data.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def get_book(db: AsyncSession, book_id: int) -> Book:
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


async def list_books(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Book]:
    result = await db.execute(select(Book).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_book(db: AsyncSession, book_id: int, data: BookUpdate) -> Book:
    book = await get_book(db, book_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    await db.commit()
    await db.refresh(book)
    return book


async def delete_book(db: AsyncSession, book_id: int) -> None:
    book = await get_book(db, book_id)
    await db.delete(book)
    await db.commit()
