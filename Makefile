.PHONY: dev db migrate test logs down

dev:
	docker compose up --build

db:
	docker compose up db redis

migrate:
	docker compose exec api alembic upgrade head

test:
	docker compose exec api pytest

logs:
	docker compose logs -f api

down:
	docker compose down
