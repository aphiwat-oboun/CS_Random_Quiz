#!/bin/bash
# Build script for Vercel Deployment
echo "=========================================="
echo "Installing Python Dependencies..."
echo "=========================================="
python3 -m pip install -r requirements.txt

echo "=========================================="
echo "Collecting Static Files..."
echo "=========================================="
python3 manage.py collectstatic --noinput --clear

echo "=========================================="
echo "Running Migrations and Seeding Data..."
echo "=========================================="
python3 manage.py migrate --noinput
python3 manage.py seed_data

echo "=========================================="
echo "Vercel Build Completed Successfully!"
echo "=========================================="
