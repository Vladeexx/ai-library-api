# Skill: Add CRUD Endpoint

## Purpose
Guides the Builder on adding a new set of CRUD API endpoints for a resource in this project.

## Trigger
- Goal contains "crud", "endpoint", "router", or "route"

## Steps
- Inspect existing routers in app/api/v1/ to follow naming and structure patterns
- Create app/api/v1/<resource>.py with POST, GET (list), GET (id), PUT, DELETE handlers
- Create app/schemas/<resource>.py with Create, Update, and Read schema classes
- Delegate all database logic to app/services/<resource>.py
- Register the new router in app/api/v1/router.py using include_router
- Add tests in tests/test_<resource>.py using the async client fixture

## Conventions
- Router files live in app/api/v1/ and are registered in app/api/v1/router.py
- Route handlers must be thin — delegate to a service module, not inline logic
- Schemas follow the three-class pattern: <Resource>Create, <Resource>Update, <Resource>Read
- Read schemas set from_attributes = True in model_config
- Tests use async def and the client fixture from tests/conftest.py

## Constraints
- Do not add business logic inside route handler functions
- Do not create models without a corresponding Alembic migration
- Do not skip tests for new endpoints
- Do not hardcode database IDs in tests — use the id from the create response
