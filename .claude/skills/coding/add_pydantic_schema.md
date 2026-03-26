# Skill: Add Pydantic Schema

## Purpose

Guides the Builder on adding Pydantic v2 request/response schemas for a resource.

## Planned usage

For each resource, this skill covers the standard three-schema pattern:
- `{Resource}Create` — fields required at creation time
- `{Resource}Update` — all fields optional for partial updates
- `{Resource}Read` — full response shape including `id`, `created_at`, `updated_at`

All schemas live in `app/schemas/`. `{Resource}Read` must set `model_config = {"from_attributes": True}`.

## Status

Scaffold only — not yet implemented.
