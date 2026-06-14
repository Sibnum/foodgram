#!/bin/bash
set -e

cd foodgram/

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Import ingredients..."
python manage.py import_data

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 foodgram.wsgi