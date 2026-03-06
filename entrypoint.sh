#!/bin/sh

set -e

echo "Applying database migrations..."
uv run python manage.py migrate --noinput

if [ "$DJANGO_DEBUG" = "True" ]; then
    echo "Starting development server..."
    exec uv run python manage.py runserver 0.0.0.0:8000
else
    echo "Starting gunicorn..."
    exec uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000
fi
