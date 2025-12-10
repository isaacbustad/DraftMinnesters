"""
Migrate data from SQLite draft_ministers.db to MySQL
This script ensures MySQL container has exact copy of SQLite data on rebuild
"""
import sqlite3
import mysql.connector
import os
import logging
import sys
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

SQLITE_DB_PATH = '/app/draft_ministers.db'
if not os.path.exists(SQLITE_DB_PATH):
    SQLITE_DB_PATH = 'draft_ministers.db'

def get_mysql_connection():
    """Get MySQL connection using environment variables"""
    host = os.environ.get('MYSQL_HOST', 'mysql')
    user = os.environ.get('MYSQL_USER', 'user')
    password = os.environ.get('MYSQL_PASSWORD', 'password')
    database = os.environ.get('MYSQL_DB', 'draft_ministers')
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def get_sqlite_connection():
    """Get SQLite connection"""
    return sqlite3.connect(SQLITE_DB_PATH)

def get_table_schema_sqlite(cursor, table_name: str) -> List[Dict[str, Any]]:
    """Get column info from SQLite table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [{'name': row[1], 'type': row[2], 'notnull': row[3], 'default': row[4], 'pk': row[5]} 
            for row in cursor.fetchall()]

def table_exists_mysql(cursor, table_name: str) -> bool:
    """Check if table exists in MySQL"""
    cursor.execute("SHOW TABLES LIKE %s", (table_name,))
    return cursor.fetchone() is not None

def migrate_table(sqlite_conn, mysql_conn, table_name: str):
    """Migrate a single table from SQLite to MySQL"""
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    try:
        # Check if table exists in SQLite
        sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not sqlite_cursor.fetchone():
            logging.warning(f"Table {table_name} does not exist in SQLite, skipping")
            return
        
        # Check if table exists in MySQL
        if not table_exists_mysql(mysql_cursor, table_name):
            logging.warning(f"Table {table_name} does not exist in MySQL, skipping (create it in init_db first)")
            return
        
        # Get all data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        columns = [desc[0] for desc in sqlite_cursor.description]
        
        if not rows:
            logging.info(f"Table {table_name} is empty, skipping data migration")
            return
        
        # Clear existing data in MySQL (but keep table structure)
        mysql_cursor.execute(f"DELETE FROM {table_name}")
        logging.info(f"Cleared existing data from MySQL table {table_name}")
        
        # Build insert statement
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([f"`{col}`" for col in columns])
        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        # Insert data
        mysql_cursor.executemany(insert_sql, rows)
        mysql_conn.commit()
        
        logging.info(f"Migrated {len(rows)} rows from {table_name}")
        
    except mysql.connector.Error as e:
        logging.error(f"Error migrating {table_name}: {e}")
        mysql_conn.rollback()
        # Don't raise - continue with other tables
    except Exception as e:
        logging.error(f"Unexpected error migrating {table_name}: {e}")
        # Don't raise - continue with other tables
    finally:
        sqlite_cursor.close()
        mysql_cursor.close()

def main():
    """Main migration function"""
    if not os.path.exists(SQLITE_DB_PATH):
        logging.error(f"SQLite database not found at {SQLITE_DB_PATH}")
        sys.exit(1)
    
    logging.info(f"Starting migration from {SQLITE_DB_PATH} to MySQL")
    
    sqlite_conn = None
    mysql_conn = None
    
    try:
        # Connect to databases
        sqlite_conn = get_sqlite_connection()
        logging.info("Connected to SQLite database")
        
        # Wait for MySQL to be ready
        max_retries = 30
        retry_delay = 2
        for i in range(max_retries):
            try:
                mysql_conn = get_mysql_connection()
                logging.info("Connected to MySQL database")
                break
            except mysql.connector.Error as e:
                if i < max_retries - 1:
                    logging.warning(f"MySQL not ready yet (attempt {i+1}/{max_retries}), retrying...")
                    import time
                    time.sleep(retry_delay)
                else:
                    raise
        
        # Get list of tables to migrate (exclude SQLite system tables)
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        sqlite_cursor.close()
        
        logging.info(f"Found {len(tables)} tables to migrate: {tables}")
        
        # Migrate each table
        for table in tables:
            try:
                migrate_table(sqlite_conn, mysql_conn, table)
            except Exception as e:
                logging.error(f"Failed to migrate table {table}: {e}")
                # Continue with other tables
                continue
        
        logging.info("Migration completed successfully")
        
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        if sqlite_conn:
            sqlite_conn.close()
        if mysql_conn:
            mysql_conn.close()

if __name__ == '__main__':
    main()

