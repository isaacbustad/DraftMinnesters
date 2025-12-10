#!/bin/bash
set -e

echo "Initializing database..."
python init_db.py

echo "Migrating data from SQLite to MySQL..."
python migrate_sqlite_to_mysql.py

echo "Starting application..."
exec python app.py
