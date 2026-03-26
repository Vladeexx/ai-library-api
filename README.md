# AI Library API

A backend REST API for managing books, built with FastAPI, PostgreSQL, and Redis. Includes Docker, Alembic migrations, pytest tests, and a Makefile-based developer workflow. Designed to be extended with features such as recommendations in future iterations.

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
| `make dev` | Build and start the long-running services: api, db, redis |
| `make db` | Start only db and redis |
| `make migrate` | One-shot: run `alembic upgrade head` via the migrate container |
| `make test` | One-shot: run pytest via a temporary api container |
| `make logs` | Tail API container logs |
| `make down` | Stop all containers |

`make dev` does not run migrations automatically — run `make migrate` first.

## Running with Docker

**Recommended workflow:**

```bash
# 1. Configure environment
cp .env.example .env

# 2. Start db and redis (detached)
make db

# 3. Apply migrations (one-shot)
make migrate

# 4. Start the API (detached)
make dev

# 5. Run tests (one-shot, no running stack required)
make test

# 6. Stop everything
make down
```

Both `make db` and `make dev` start services in detached mode — use `make logs` to follow API output. The API is available at http://localhost:8000 once started.

Hot-reload is enabled via the mounted volume. To also remove the database volume on teardown:

```bash
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

## Development Notes

This project was developed with the assistance of AI tools (ChatGPT and Claude Code) to accelerate implementation and explore different approaches during development.

All architectural decisions, system design, validation, and final integration were performed by the author. The tools were used primarily as productivity aids, similar to how engineers use documentation, reference materials, or developer tools.

The final system was implemented, verified, and tested end-to-end by the author, including containerized setup, database migrations, API functionality, and automated tests.
