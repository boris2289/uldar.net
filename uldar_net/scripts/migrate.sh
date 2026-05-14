#!/bin/bash
set -e

echo "Making migrations"
docker compose exec django python manage.py makemigrations

echo "Applying migrations"
docker compose exec django python manage.py migrate

echo "Done."