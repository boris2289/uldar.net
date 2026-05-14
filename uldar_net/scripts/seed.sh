#!/bin/bash
set -e

echo "Seeding database"
docker compose exec django python manage.py seed --flush

echo "Done."