#!/bin/bash
set -e

echo "Running flake8"
docker compose exec django flake8 apps/ settings/

echo "Checking import order with isort"
docker compose exec django isort --check-only --diff apps/ settings/

echo "Lint done"