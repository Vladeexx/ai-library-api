from fastapi import APIRouter

from app.api.v1 import books

router = APIRouter(prefix="/api/v1")
router.include_router(books.router)
