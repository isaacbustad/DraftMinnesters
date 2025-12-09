import json
import os
import base64
import logging
import requests
from kafka import KafkaConsumer
from cassandra.cluster import Cluster

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Configuration
KAFKA_TOPIC = 'football_stream'
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
CASSANDRA_HOSTS = os.environ.get('CASSANDRA_HOSTS', 'localhost').split(',')
SHARED_DATA_DIR = '/shared_data'
BANNERS_DIR = os.path.join(SHARED_DATA_DIR, 'banners')
DATA_DIR = os.path.join(SHARED_DATA_DIR, 'data')

# Ensure directories exist
os.makedirs(BANNERS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def setup_cassandra():
    try:
        cluster = Cluster(CASSANDRA_HOSTS)
        session = cluster.connect()
        
        # Create Keyspace
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS draft_ministers 
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        
        session.set_keyspace('draft_ministers')
        
        # Create Table
        session.execute("""
            CREATE TABLE IF NOT EXISTS team_banners (
                team_id int PRIMARY KEY,
                team_name text,
                banner_path text,
                banner_image blob
            )
        """)
        
        return session
    except Exception as e:
        logging.error(f"Failed to connect/setup Cassandra: {e}")
        return None

def download_and_save_image(team_id, url):
    if not url:
        return None, None
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            image_data = response.content
            filename = f"{team_id}.png"
            filepath = os.path.join(BANNERS_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(image_data)
                
            return filepath, image_data
        else:
            logging.warning(f"Failed to download image from {url}: {response.status_code}")
            return None, None
    except Exception as e:
        logging.error(f"Error downloading image for team {team_id}: {e}")
        return None, None

def save_json(match_data):
    try:
        match_id = match_data.get('match_id')
        filepath = os.path.join(DATA_DIR, f"match_{match_id}.json")
        
        with open(filepath, "w") as f:
            json.dump(match_data, f)
            
    except Exception as e:
        logging.error(f"Failed to save JSON: {e}")

def run_consumer():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    session = setup_cassandra()
    if not session:
        logging.error("Cassandra session not available. Exiting.")
        return

    logging.info("Consumer started. Waiting for messages...")

    for message in consumer:
        data = message.value
        logging.info(f"Received match: {data['match_id']}")
        
        # Process Home Team
        home_team = data.get('home_team')
        if home_team:
            banner_path, image_data = download_and_save_image(home_team['id'], home_team.get('banner_url'))
            
            if banner_path and image_data:
                try:
                    query = "INSERT INTO team_banners (team_id, team_name, banner_path, banner_image) VALUES (%s, %s, %s, %s)"
                    session.execute(query, (home_team['id'], home_team['name'], banner_path, image_data))
                except Exception as e:
                    logging.error(f"Cassandra insert failed: {e}")

        # Process Away Team
        away_team = data.get('away_team')
        if away_team:
            banner_path, image_data = download_and_save_image(away_team['id'], away_team.get('banner_url'))
            
            if banner_path and image_data:
                try:
                    query = "INSERT INTO team_banners (team_id, team_name, banner_path, banner_image) VALUES (%s, %s, %s, %s)"
                    session.execute(query, (away_team['id'], away_team['name'], banner_path, image_data))
                except Exception as e:
                    logging.error(f"Cassandra insert failed: {e}")

        # Save full match JSON to shared volume
        save_json(data)

if __name__ == "__main__":
    run_consumer()
