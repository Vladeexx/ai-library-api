# Skill: Fix Pydantic Settings Env Error

## Purpose

Guides the Fixer on resolving validation errors raised by `pydantic-settings` when loading environment variables.

## Planned usage

Known patterns in this project:
- Extra env vars (e.g. `POSTGRES_USER`) rejected because `extra` is not set to `"ignore"` — fix: add `"extra": "ignore"` to `model_config` in `app/core/config.py`
- A required field (e.g. `DATABASE_URL`) missing from `.env` — fix: ensure `.env` is copied from `.env.example` and all required keys are present
- Wrong type for a field (e.g. `DEBUG=yes` instead of `DEBUG=true`) — fix: use `true`/`false` for boolean fields

## Status

Scaffold only — not yet implemented.
