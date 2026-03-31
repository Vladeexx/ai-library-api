# Skill: Fix Pydantic Settings Env Error

## Purpose
Guides the Fixer on resolving validation errors raised by pydantic-settings when loading environment variables.

## Trigger
- Goal contains "settings", "config", or "env"

## Steps
- Check app/core/config.py for model_config — ensure extra = "ignore" is set
- Check .env exists and contains all keys from .env.example
- Verify boolean fields use true or false, not yes, no, 1, or 0
- Verify DATABASE_URL and other required fields are present and correctly formatted
- Re-run tests to confirm the validation error is resolved

## Conventions
- pydantic-settings reads from environment variables and .env automatically
- model_config = {"extra": "ignore"} prevents errors from unexpected env vars
- Boolean values must be true or false (lowercase strings), not yes/no or 1/0

## Constraints
- Do not hardcode secrets in app/core/config.py — use environment variables
- Do not add required fields to Settings without updating .env.example
- Do not set extra = "forbid" — this project uses extra = "ignore"
