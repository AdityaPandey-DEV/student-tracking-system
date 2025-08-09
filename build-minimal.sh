#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip first
pip install --upgrade pip

# Install minimal dependencies first
pip install -r requirements-minimal.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
