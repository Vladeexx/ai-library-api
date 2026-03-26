# Skill: Run Migrations

## Purpose

Guides the Builder or Orchestrator on applying database migrations in this project.

## Planned usage

- Command: `make migrate` (runs `docker compose run --rm migrate`)
- Requires `db` service to be healthy before running
- Migrations live in `alembic/versions/`
- To roll back one step: `docker compose run --rm migrate alembic downgrade -1`

## Status

Scaffold only — not yet implemented.
