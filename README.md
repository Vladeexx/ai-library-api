# AI Library API

A backend REST API for managing books and recommendations, built with FastAPI, PostgreSQL, and Redis.

## Architecture

```
HTTP Request → Router → Service → Database/Cache
```

- **Routers** (`app/api/v1/`) — HTTP concerns only: request parsing, response shaping, status codes
- **Services** (`app/services/`) — business logic and database queries
- **Models** (`app/models/`) — SQLAlchemy ORM definitions
- **Schemas** (`app/schemas/`) — Pydantic models for validation and serialization
- **Core** (`app/core/`) — configuration, database session, Redis client

## Project Structure

```
app/
├── api/v1/         # API routes
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
└── core/           # Config, DB, Redis

alembic/            # Database migrations
tests/              # pytest test suite
```

## Running Locally

**Prerequisites:** Python 3.11, PostgreSQL, Redis

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env

# 3. Run database migrations
alembic upgrade head

# 4. Start the API
uvicorn app.main:app --reload
```

API available at http://localhost:8000
Interactive docs at http://localhost:8000/docs

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make dev` | Build and start the full stack (api, db, redis) |
| `make db` | Start only db and redis |
| `make migrate` | Run `alembic upgrade head` inside the api container |
| `make test` | Run pytest inside the api container |
| `make logs` | Tail API container logs |
| `make down` | Stop all containers |

## Running with Docker

```bash
cp .env.example .env
docker compose up --build
```

Postgres and Redis health checks gate the API startup. Hot-reload is enabled via the mounted volume.

```bash
# Stop and remove volumes
docker compose down -v
```

## Database Migrations

```bash
# Apply all migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Generate a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# View migration history
alembic history
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/books/` | Create a book |
| `GET` | `/api/v1/books/` | List books (supports `skip` and `limit`) |
| `GET` | `/api/v1/books/{id}` | Get a book by ID |
| `PUT` | `/api/v1/books/{id}` | Update a book |
| `DELETE` | `/api/v1/books/{id}` | Delete a book |

## Running Tests

```bash
pip install -r requirements.txt
pytest
```

Tests use an in-memory SQLite database and mock Redis — no running services required.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `APP_NAME` | Application name |
| `DEBUG` | Enable debug mode (`true`/`false`) |
| `DATABASE_URL` | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `POSTGRES_USER` | Postgres user (docker-compose only) |
| `POSTGRES_PASSWORD` | Postgres password (docker-compose only) |
| `POSTGRES_DB` | Postgres database name (docker-compose only) |
| `REDIS_URL` | Redis connection URL |
