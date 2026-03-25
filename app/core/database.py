from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    # Import models so their metadata is registered before create_all runs.
    import app.models.book  # noqa: F401

    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
