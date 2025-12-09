#!/bin/bash
set -e

echo "Initializing database..."
python init_db.py

echo "Starting application..."
exec python app.py
