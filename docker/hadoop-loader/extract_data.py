import sqlite3
import csv
import os
import sys

# Connect to database
# We expect the database to be mounted at /data/football_database.sqlite
DB_PATH = '/data/football_database.sqlite'
OUTPUT_PATH = 'matches.csv'

def extract_data():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        sys.exit(1)
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Select relevant columns
        query = """
        SELECT id, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal 
        FROM Match
        WHERE home_team_goal IS NOT NULL AND away_team_goal IS NOT NULL
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['id', 'date', 'home_team_api_id', 'away_team_api_id', 'home_team_goal', 'away_team_goal'])
            writer.writerows(rows)
            
        print(f"Successfully extracted {len(rows)} matches to {OUTPUT_PATH}")
        conn.close()
        
    except Exception as e:
        print(f"Error extracting data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    extract_data()
