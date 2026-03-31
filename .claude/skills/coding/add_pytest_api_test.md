# Skill: Add pytest API Test

## Purpose
Guides the Builder on adding integration tests for a new API endpoint.

## Trigger
- Goal contains "test" or "tests"
- A new endpoint was just added and tests are needed

## Steps
- Create tests/test_<resource>.py for the resource being tested
- Import the client fixture — it is provided automatically via tests/conftest.py
- Write async def test functions (no @pytest.mark.asyncio decorator needed)
- Test at minimum: create, retrieve by id, list, and 404 not found
- Assert both the response status code and the returned JSON fields
- Run with in-memory SQLite — no Docker or external services required

## Conventions
- Test files live in tests/ and are named test_<resource>.py
- All test functions use async def — asyncio_mode = auto is set in pytest config
- The client fixture provides an AsyncClient pointed at the test app
- Tests run against in-memory SQLite — no docker-compose needed for test runs

## Constraints
- Do not use synchronous test functions with async endpoints
- Do not hardcode test data IDs — rely on the id field from the create response
- Do not mock the database in these tests — use the real in-memory SQLite fixture
