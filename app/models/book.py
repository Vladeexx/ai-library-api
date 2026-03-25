from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    synopsis: Mapped[str | None] = mapped_column(Text, nullable=True)
