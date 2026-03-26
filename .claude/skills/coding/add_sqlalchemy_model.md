# Skill: Add SQLAlchemy Model

## Purpose

Guides the Builder on adding a new SQLAlchemy ORM model to the project.

## Planned usage

When a new database table is required, this skill covers:
- Creating a file in `app/models/`
- Inheriting from `Base` and `TimestampMixin` (defined in `app/models/base.py`)
- Defining columns using `Mapped` and `mapped_column`
- Importing the model in `alembic/env.py` to register its metadata

## Status

Scaffold only — not yet implemented.
