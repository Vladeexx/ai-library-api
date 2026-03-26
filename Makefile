.PHONY: dev db migrate test logs down

dev:
	docker compose up --build

db:
	docker compose up db redis

migrate:
	docker compose run --rm migrate

test:
	docker compose run --rm api pytest

logs:
	docker compose logs -f api

down:
	docker compose down
