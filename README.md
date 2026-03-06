# Task Tracker API

REST API for task management built with Django + DRF and JWT authentication.

## Stack

- Python 3.13, Django 6, DRF
- PostgreSQL 17
- JWT (simplejwt)
- Swagger (drf-spectacular)
- Docker & Docker Compose
- uv (package manager)

## Getting Started

```bash
cp .env.example .env
make start-rebuild
```

API documentation is available at `http://localhost:8000/api/docs/`.

## Commands

### Development

| Command                | Description                   |
|------------------------|-------------------------------|
| `make build`           | Build Docker image            |
| `make start-rebuild`   | Build and start containers    |
| `make up-detached`     | Start containers in background |
| `make down`            | Stop containers               |
| `make restart`         | Restart the web container     |
| `make logs`            | Tail web server logs          |
| `make make-migrations` | Generate new migrations       |
| `make migrate`         | Apply database migrations     |
| `make createsuperuser` | Create a superuser            |
| `make test`            | Run tests                     |
| `make shell`           | Open Django shell             |

### Production

| Command          | Description                          |
|------------------|--------------------------------------|
| `make prod-build`| Build production Docker image        |
| `make prod-up`   | Start production containers          |
| `make prod-down` | Stop production containers           |

> In development (`DJANGO_DEBUG=True`), the app runs with Django's dev server and auto-reloads on code changes. In production (`DJANGO_DEBUG=False`), it runs with Gunicorn.

## API Endpoints

| Method | URL                   | Description                                  |
|--------|-----------------------|----------------------------------------------|
| POST   | `/api/register/`      | Register a new user                          |
| POST   | `/api/token/`         | Obtain a JWT token pair                      |
| POST   | `/api/token/refresh/` | Refresh a JWT access token                   |
| GET    | `/api/tasks/`         | List tasks (filter with `?status=true/false`) |
| POST   | `/api/tasks/`         | Create a task                                |
| GET    | `/api/tasks/<id>/`    | Retrieve a task                              |
| PUT    | `/api/tasks/<id>/`    | Update a task                                |
| PATCH  | `/api/tasks/<id>/`    | Partially update a task                      |
| DELETE | `/api/tasks/<id>/`    | Delete a task                                |

## HTTP Requests (PyCharm)

The `http_requests/` directory contains `.http` files for testing the API directly from PyCharm's HTTP Client.

- `auth.http` — Registration, JWT token obtain/refresh, error cases
- `tasks.http` — Full task CRUD lifecycle with assertions

To use them, select the **dev** environment in PyCharm's HTTP Client and run `auth.http` first to register a user and obtain a token, then run `tasks.http` for task operations.
