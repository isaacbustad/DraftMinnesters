import sqlite3
import mysql.connector
import os
import logging
import json
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

SQLITE_DB = 'draft_ministers.db'

def migrate_teams(sqlite_conn, mysql_conn):
    logging.info("Migrating soccer_teams...")
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    sqlite_cursor.execute("SELECT * FROM soccer_teams")
    rows = sqlite_cursor.fetchall()
    
    # Get column names from sqlite
    col_names = [description[0] for description in sqlite_cursor.description]
    
    count = 0
    for row in rows:
        row_dict = dict(zip(col_names, row))
        
        # Prepare insert statement
        placeholders = ', '.join(['%s'] * len(col_names))
        columns = ', '.join(col_names)
        sql = f"REPLACE INTO soccer_teams ({columns}) VALUES ({placeholders})"
        
        values = list(row)
        # Handle boolean conversion for 'national' if needed, though MySQL handles 0/1 fine
        
        try:
            mysql_cursor.execute(sql, values)
            count += 1
        except mysql.connector.Error as err:
            logging.error(f"Error inserting team {row_dict.get('name')}: {err}")
            
    mysql_conn.commit()
    logging.info(f"Migrated {count} teams.")

def migrate_fixtures(sqlite_conn, mysql_conn):
    logging.info("Migrating soccer_fixtures...")
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    sqlite_cursor.execute("SELECT * FROM soccer_fixtures")
    rows = sqlite_cursor.fetchall()
    col_names = [description[0] for description in sqlite_cursor.description]
    
    count = 0
    for row in rows:
        row_dict = dict(zip(col_names, row))
        
        # Handle raw_data JSON
        # In SQLite it's a string, in MySQL it's JSON type (which accepts string or dict)
        # No conversion needed usually if passing string
        
        placeholders = ', '.join(['%s'] * len(col_names))
        columns = ', '.join(col_names)
        sql = f"REPLACE INTO soccer_fixtures ({columns}) VALUES ({placeholders})"
        
        values = list(row)
        
        try:
            mysql_cursor.execute(sql, values)
            count += 1
        except mysql.connector.Error as err:
            logging.error(f"Error inserting fixture {row_dict.get('fixture_id')}: {err}")
            
    mysql_conn.commit()
    logging.info(f"Migrated {count} fixtures.")

def migrate_config(sqlite_conn, mysql_conn):
    logging.info("Migrating app_config...")
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    sqlite_cursor.execute("SELECT * FROM app_config")
    rows = sqlite_cursor.fetchall()
    
    count = 0
    for row in rows:
        key, value = row
        try:
            mysql_cursor.execute("REPLACE INTO app_config (`key`, value) VALUES (%s, %s)", (key, value))
            count += 1
        except mysql.connector.Error as err:
            logging.error(f"Error inserting config {key}: {err}")
            
    mysql_conn.commit()
    logging.info(f"Migrated {count} config items.")

def main():
    if not os.path.exists(SQLITE_DB):
        logging.error(f"SQLite database file {SQLITE_DB} not found.")
        return

    try:
        logging.info("Connecting to databases...")
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        mysql_conn = get_db_connection()
        
        # Ensure tables exist in MySQL (init_db logic should have run by app, but we can't rely on it running first)
        # For simplicity, we assume the app container has started and initialized the DB, 
        # or we could import init_db. But init_db is in app.py which starts the server.
        # Let's assume the user runs this AFTER starting the containers.
        
        migrate_teams(sqlite_conn, mysql_conn)
        migrate_fixtures(sqlite_conn, mysql_conn)
        migrate_config(sqlite_conn, mysql_conn)
        
        logging.info("Migration completed successfully.")
        
    except Exception as e:
        logging.error(f"Migration failed: {e}")
    finally:
        if 'sqlite_conn' in locals(): sqlite_conn.close()
        if 'mysql_conn' in locals(): mysql_conn.close()

if __name__ == "__main__":
    main()
