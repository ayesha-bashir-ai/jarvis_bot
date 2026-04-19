.PHONY: help build up down logs clean test backup

help:
	@echo "JARVIS AI Assistant Commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make clean    - Clean up containers and volumes"
	@echo "  make test     - Run tests"
	@echo "  make backup   - Backup database"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "JARVIS AI Assistant is running!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

test:
	pytest tests/ -v --cov=backend --cov-report=html

backup:
	@mkdir -p backups
	@cp data/jarvis.db backups/jarvis_$(shell date +%Y%m%d_%H%M%S).db
	@echo "Database backed up"

init:
	@mkdir -p data logs
	@python scripts/init_db.py
	@echo "Initialization complete"

dev:
	@docker-compose up