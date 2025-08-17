#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Generate fresh PostgreSQL-compatible migrations
echo "Creating fresh migrations for PostgreSQL..."
python manage.py makemigrations accounts --noinput
python manage.py makemigrations timetable --noinput
python manage.py makemigrations ai_features --noinput

# Apply migrations
echo "Applying migrations to PostgreSQL database..."
python manage.py migrate --noinput

# Verify database tables exist
echo "Verifying database tables..."
python manage.py showmigrations

# Create default admin and sample data
echo "Creating default admin user..."
python manage.py create_default_superuser

echo "Populating sample data..."
python manage.py populate_realistic_data

echo "Build completed successfully!"
