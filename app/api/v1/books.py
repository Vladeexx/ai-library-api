from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(data: BookCreate, db: AsyncSession = Depends(get_db)):
    return await book_service.create_book(db, data)


@router.get("/", response_model=list[BookRead])
async def list_books(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    return await book_service.list_books(db, skip=skip, limit=limit)


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    return await book_service.get_book(db, book_id)


@router.put("/{book_id}", response_model=BookRead)
async def update_book(book_id: int, data: BookUpdate, db: AsyncSession = Depends(get_db)):
    return await book_service.update_book(db, book_id, data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    await book_service.delete_book(db, book_id)
