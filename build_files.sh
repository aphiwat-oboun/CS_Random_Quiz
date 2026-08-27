#!/bin/bash
# Build script for Vercel Deployment

echo "=========================================="
echo "Installing Python Dependencies..."
echo "=========================================="
python3 -m pip install --break-system-packages -r requirements.txt

echo "=========================================="
echo "Creating Static Directory & Collecting..."
echo "=========================================="
mkdir -p staticfiles_build/static
python3 manage.py collectstatic --noinput --clear

echo "=========================================="
echo "Running Migrations & Seeding Initial Data..."
echo "=========================================="
python3 manage.py migrate --noinput
python3 manage.py seed_data

echo "=========================================="
echo "Vercel Build Completed Successfully!"
echo "=========================================="
