from app import init_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

if __name__ == "__main__":
    logging.info("Starting manual database initialization...")
    try:
        init_db()
        logging.info("Database initialization completed.")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
