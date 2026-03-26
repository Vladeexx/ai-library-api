# Skill: Add pytest API Test

## Purpose

Guides the Builder on adding integration tests for a new API endpoint.

## Planned usage

When a new endpoint is added, this skill covers:
- Using the `client` fixture from `tests/conftest.py`
- Writing `async def` test functions (no `@pytest.mark.asyncio` decorator required — `asyncio_mode = auto`)
- Testing create, retrieve, list, and 404 cases as a minimum
- Relying on the in-memory SQLite DB — no running services needed

## Status

Scaffold only — not yet implemented.
