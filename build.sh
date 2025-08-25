#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies with faster pip options
pip install -r requirements.txt --no-cache-dir --disable-pip-version-check

# Create media directory if it doesn't exist
mkdir -p media

# Collect static files with optimization
python manage.py collectstatic --no-input --clear

# Run database migrations
python manage.py migrate --noinput
