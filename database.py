import mysql.connector
import os
import time
import logging

def get_db_connection(retries=20, delay=3):
    """
    Establish a connection to the MySQL database.
    Retries if the connection fails (useful for container startup).
    """
    host = os.environ.get('MYSQL_HOST', 'localhost')
    user = os.environ.get('MYSQL_USER', 'user')
    password = os.environ.get('MYSQL_PASSWORD', 'password')
    database = os.environ.get('MYSQL_DB', 'draft_ministers')
    
    # If running locally without env vars set, might default to localhost with different creds
    # But for now we assume env vars or these defaults.

    for i in range(retries):
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            return conn
        except mysql.connector.Error as err:
            logging.warning(f"Database connection failed (attempt {i+1}/{retries}): {err}")
            if i < retries - 1:
                time.sleep(delay)
            else:
                logging.error("Could not connect to database after multiple attempts.")
                raise err
