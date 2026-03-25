# AI Library API - Claude Instructions

This repository contains a backend API for managing books and recommendations.

## Technology Stack

- Python 3.11
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic
- Docker
- pytest

## Project Structure

app/
- api/ → API routes
- models/ → database models
- services/ → business logic
- core/ → configuration and shared utilities

tests/
- unit and integration tests

infra/
- infrastructure (Terraform / cloud deployment)

## Coding Guidelines

- Keep code modular and clean
- Use type hints
- Follow FastAPI best practices
- Use environment variables for configuration
- Separate API routes from business logic

## Tasks Claude May Perform

Claude may:
- generate FastAPI endpoints
- create SQLAlchemy models
- write tests
- update Docker configuration
- improve documentation

Claude should:
- explain major architectural decisions
- keep changes minimal and focused
- avoid unnecessary complexity