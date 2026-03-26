# Skill: Run Tests

## Purpose

Guides the Tester on running the test suite and interpreting results.

## Planned usage

- Command: `make test` (runs `docker compose run --rm api pytest`)
- Tests use an in-memory SQLite database — no running stack required
- A non-zero exit code means failures; output is captured and forwarded to the Fixer
- To run a specific test file: `docker compose run --rm api pytest tests/test_books_api.py`

## Status

Scaffold only — not yet implemented.
