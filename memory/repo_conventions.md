# Repository Conventions

This file documents project conventions the Builder agent must follow when generating or modifying code.

## Language and runtime

- Python 3.11
- Async throughout — use `async def` and `await` for all I/O

## Framework patterns

- FastAPI routers live in `app/api/v1/` and are registered in `app/api/v1/router.py`
- Route handlers must be thin — all logic belongs in `app/services/`
- Database session is injected via `Depends(get_db)` from `app/core/database.py`

## Models

- All models inherit from `Base` and `TimestampMixin` (defined in `app/models/base.py`)
- Use `Mapped` and `mapped_column` for column definitions (SQLAlchemy 2.x style)
- New models must be imported in `alembic/env.py` and `tests/conftest.py`

## Schemas

- Three schemas per resource: `{Resource}Create`, `{Resource}Update`, `{Resource}Read`
- `{Resource}Update` uses all-optional fields for partial updates
- `{Resource}Read` sets `model_config = {"from_attributes": True}`

## Tests

- Tests use `async def` — no `@pytest.mark.asyncio` decorator needed (`asyncio_mode = auto`)
- Use the `client` fixture from `tests/conftest.py`
- In-memory SQLite via `aiosqlite` — no running services required

## Configuration

- All settings loaded via `app/core/config.py` using `pydantic-settings`
- `model_config` includes `"extra": "ignore"` to allow docker-compose env vars

## Status

Scaffold only — to be expanded as the agent loop runs.
