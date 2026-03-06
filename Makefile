.PHONY: build up down restart logs make-migrations migrate createsuperuser test shell \
       start-rebuild up-detached prod-build prod-up prod-down

# Development
build:
	docker compose build

up-detached:
	docker compose up -d

start-rebuild:
	docker compose up --build

down:
	docker compose down

restart:
	docker compose restart web

logs:
	docker compose logs -f web

make-migrations:
	docker compose exec web uv run python manage.py makemigrations

migrate:
	docker compose exec web uv run python manage.py migrate

createsuperuser:
	docker compose exec web uv run python manage.py createsuperuser

test:
	docker compose exec web uv run python manage.py test

shell:
	docker compose exec web uv run python manage.py shell

# Production
prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down
