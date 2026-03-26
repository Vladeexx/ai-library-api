# Skill: Add Alembic Migration

## Purpose

Guides the Builder on generating and validating a new Alembic migration after a model change.

## Planned usage

After a SQLAlchemy model is added or modified:
1. Ensure the model is imported in `alembic/env.py`
2. Run `alembic revision --autogenerate -m "describe the change"`
3. Review the generated file in `alembic/versions/` for correctness
4. Apply with `alembic upgrade head` (or `make migrate`)

## Status

Scaffold only — not yet implemented.
