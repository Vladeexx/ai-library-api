from datetime import datetime

from pydantic import BaseModel, Field


class BookBase(BaseModel):
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    isbn: str | None = Field(None, max_length=20)
    published_year: int | None = Field(None, ge=1000, le=9999)
    synopsis: str | None = None


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    author: str | None = Field(None, max_length=255)
    isbn: str | None = Field(None, max_length=20)
    published_year: int | None = Field(None, ge=1000, le=9999)
    synopsis: str | None = None


class BookRead(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
