# Skill: Fix Import Error

## Purpose

Guides the Fixer on diagnosing and resolving Python import errors in this project.

## Planned usage

Common causes in this codebase:
- A new model not added to `alembic/env.py` or `tests/conftest.py`
- A missing `__init__.py` in a new package directory
- A circular import between `app/core/` and `app/models/`
- A module renamed without updating all import sites

## Status

Scaffold only — not yet implemented.
