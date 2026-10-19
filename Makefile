.PHONY: help build up down down-v logs ps migrate test test-local run-local clean

help:
	@echo "FastAPI Demo - Available Makefile Commands:"
	@echo "  make build       - Build or rebuild Docker images"
	@echo "  make up          - Start API and MySQL containers in background"
	@echo "  make down        - Stop containers without removing MySQL data"
	@echo "  make down-v      - Stop containers and permanently delete MySQL volume"
	@echo "  make logs        - Tail live logs from the API service"
	@echo "  make ps          - View status of Docker Compose services"
	@echo "  make migrate     - Run database migrations via Alembic inside Docker"
	@echo "  make test        - Run tests inside the running API container"
	@echo "  make test-local  - Run tests locally in active Python environment"
	@echo "  make run-local   - Run FastAPI server locally with Uvicorn (requires local MySQL or SQLite)"
	@echo "  make clean       - Remove cached Python bytecode and test artifacts"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f api

ps:
	docker compose ps

migrate:
	docker compose exec api alembic upgrade head

test:
	docker compose exec api pytest

test-local:
	pytest

run-local:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

