import json
import time
import sqlite3
import os
import logging
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Configuration
DB_PATH = 'draft_ministers.db'
KAFKA_TOPIC = 'football_stream'
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to SQLite DB: {e}")
        return None

def run_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    
    # Fetch teams to get logos
    cursor.execute("SELECT id, name, logo FROM soccer_teams")
    teams = {row['id']: {'name': row['name'], 'logo': row['logo']} for row in cursor.fetchall()}
    
    logging.info(f"Loaded {len(teams)} teams.")

    # Simulate live match data using fixtures
    # We'll stream matches and include team info (with banner URLs) in the payload
    cursor.execute("""
        SELECT fixture_id, date, home_team_id, away_team_id, home_goals, away_goals, season
        FROM soccer_fixtures
        WHERE status_long = 'Match Finished'
        ORDER BY date DESC
        LIMIT 100
    """)
    
    matches = cursor.fetchall()
    logging.info(f"Found {len(matches)} matches to stream.")
    
    for match in matches:
        home_team = teams.get(match['home_team_id'], {'name': 'Unknown', 'logo': None})
        away_team = teams.get(match['away_team_id'], {'name': 'Unknown', 'logo': None})
        
        payload = {
            'match_id': match['fixture_id'],
            'date': match['date'],
            'season': match['season'],
            'home_team': {
                'id': match['home_team_id'],
                'name': home_team['name'],
                'goals': match['home_team_goals'] if 'home_team_goals' in match.keys() else match['home_goals'],
                'banner_url': home_team['logo']
            },
            'away_team': {
                'id': match['away_team_id'],
                'name': away_team['name'],
                'goals': match['away_team_goals'] if 'away_team_goals' in match.keys() else match['away_goals'],
                'banner_url': away_team['logo']
            }
        }
        
        try:
            producer.send(KAFKA_TOPIC, payload)
            logging.info(f"Sent match: {home_team['name']} vs {away_team['name']}")
            time.sleep(2) # Simulate delay
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            
    conn.close()
    producer.close()

if __name__ == "__main__":
    # Wait for Kafka to be ready
    time.sleep(10) 
    run_producer()
