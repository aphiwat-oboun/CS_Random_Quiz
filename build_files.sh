#!/bin/bash
# Build script for Vercel Deployment

echo "=========================================="
echo "Installing Python Dependencies..."
echo "=========================================="
python3 -m pip install --break-system-packages -r requirements.txt

echo "=========================================="
echo "Collecting Static Files..."
echo "=========================================="
mkdir -p staticfiles
python3 manage.py collectstatic --noinput --clear

echo "=========================================="
echo "Running Database Migrations & Firebase Sync..."
echo "=========================================="
python3 manage.py migrate --noinput
python3 manage.py sync_firebase

echo "=========================================="
echo "Vercel Build Completed Successfully!"
echo "=========================================="
