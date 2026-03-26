# Skill: Add CRUD Endpoint

## Purpose

Guides the Builder on adding a new set of CRUD API endpoints for a resource in this project.

## Planned usage

When a new resource is introduced, this skill provides the standard pattern for:
- `POST /resource/` — create
- `GET /resource/` — list (with `skip` and `limit`)
- `GET /resource/{id}` — retrieve
- `PUT /resource/{id}` — update
- `DELETE /resource/{id}` — delete

## Conventions to follow

- Add router to `app/api/v1/`
- Register router in `app/api/v1/router.py`
- Keep route handlers thin — delegate logic to a service module

## Status

Scaffold only — not yet implemented.
