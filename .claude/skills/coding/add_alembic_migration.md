# Skill: Add Alembic Migration

## Purpose
Guides the Builder on generating and validating a new Alembic migration after a model change.

## Trigger
- Goal contains "migration", "migrate", or "alembic"

## Steps
- Ensure the model is imported in alembic/env.py (required for autogenerate to detect it)
- Run: alembic revision --autogenerate -m "<describe the change>"
- Review the generated file in alembic/versions/ for correctness before applying
- Apply with: make migrate (runs docker compose run --rm migrate)
- Run tests to confirm the migration does not break the test suite

## Conventions
- Migration files live in alembic/versions/ and are never edited manually after apply
- The model must be imported in alembic/env.py before autogenerate will detect it
- Migration message should describe the schema change (e.g. "add authors table")
- Use make migrate rather than running alembic commands directly

## Constraints
- Do not skip reviewing the generated migration file before applying
- Do not apply a migration that drops columns without confirming the intent
- Do not create a migration without first confirming the model import is registered
