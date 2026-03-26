# Skill: Inspect API Logs

## Purpose

Guides agents on retrieving and interpreting API container logs for debugging.

## Planned usage

- Command: `make logs` (runs `docker compose logs -f api`)
- Use to diagnose startup errors, unhandled exceptions, or unexpected 500 responses
- SQLAlchemy query logs are visible when `DEBUG=true` in `.env`
- Useful after `make dev` to confirm the API started cleanly

## Status

Scaffold only — not yet implemented.
