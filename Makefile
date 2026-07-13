.PHONY: up down api mobile test gen-client migrate

up:
	docker compose up -d db

down:
	docker compose down

migrate:
	cd api && . .venv/bin/activate && alembic upgrade head

api:
	cd api && . .venv/bin/activate && uvicorn app.main:app --reload

test:
	cd api && . .venv/bin/activate && pytest -v

gen-client:
	cd api && . .venv/bin/activate && python export_openapi.py
	cd mobile && npx openapi-typescript openapi.json -o lib/generated/api-types.ts

mobile:
	cd mobile && npx expo start
