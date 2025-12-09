from flask import Flask, jsonify, request, render_template, send_from_directory
import subprocess
import json
import requests
import logging
import os
from database import get_db_connection
from routes.matches import matches_bp, get_match_data_internal
from routes.user import user_bp
from routes.admin import admin_bp
import random

app = Flask(__name__)
app.register_blueprint(matches_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

@app.route('/shared/banners/<path:filename>')
def shared_banners(filename):
    return send_from_directory('/shared_data/banners', filename)

# Create logs directory if it doesn't exist
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler(os.path.join(log_dir, 'app.log')), logging.StreamHandler()])

def init_db():
    try:
        conn = get_db_connection()
        logging.info("Database connected successfully.")
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_teams (
                id INT PRIMARY KEY,
                name VARCHAR(255) UNIQUE,
                code VARCHAR(10),
                country VARCHAR(255),
                founded INT,
                national BOOLEAN,
                logo TEXT,
                venue_id INT,
                venue_name VARCHAR(255),
                venue_address TEXT,
                venue_city VARCHAR(255),
                venue_capacity INT,
                venue_surface VARCHAR(255),
                venue_image TEXT,
                league VARCHAR(255),
                dmr FLOAT
            )
        """)
        
        # Check if dmr column exists (MySQL specific check)
        cursor.execute("SHOW COLUMNS FROM soccer_teams LIKE 'dmr'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE soccer_teams ADD COLUMN dmr FLOAT")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_players (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                position VARCHAR(50),
                team_id INT,
                age INT,
                FOREIGN KEY (team_id) REFERENCES soccer_teams(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_fixtures (
                fixture_id INT PRIMARY KEY,
                date VARCHAR(50),
                timestamp INT,
                status_long VARCHAR(50),
                status_short VARCHAR(10),
                home_team_id INT,
                away_team_id INT,
                league_id INT,
                league_name VARCHAR(255),
                season INT,
                round VARCHAR(50),
                venue_id INT,
                venue_name VARCHAR(255),
                venue_city VARCHAR(255),
                referee VARCHAR(255),
                home_goals INT,
                away_goals INT,
                home_winner BOOLEAN,
                away_winner BOOLEAN,
                raw_data JSON,
                home_win_percentage FLOAT,
                away_win_percentage FLOAT,
                draw_percentage FLOAT
            )
        """)
        
        # Check for win percentage columns
        for col in ['home_win_percentage', 'away_win_percentage', 'draw_percentage']:
            cursor.execute(f"SHOW COLUMNS FROM soccer_fixtures LIKE '{col}'")
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE soccer_fixtures ADD COLUMN {col} FLOAT")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_run_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                run_time VARCHAR(50) NOT NULL,
                status VARCHAR(50),
                teams_updated INT DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_config (
                `key` VARCHAR(255) PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Insert default config
        cursor.execute("""
            INSERT IGNORE INTO app_config (`key`, value) 
            VALUES ('upcoming_match_cutoff_date', '2023-12-31')
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Database initialization error: {e}")
        raise e

@app.route('/')
def home():
    logging.info("Accessing home endpoint")
    
    data = get_match_data_internal()
    upcoming = []
    winner_team = None
    underdog_team = None

    if "error" not in data:
        upcoming = data.get("upcoming", [])
        
        # Winner: Team with highest win % (already sorted in most_likely_to_win)
        winners_list = data.get("most_likely_to_win", [])
        winner_match = winners_list[0] if winners_list else None
        
        if winner_match:
            home = winner_match["home_team"]
            away = winner_match["away_team"]
            winner_team = home if home["win_percentage"] >= away["win_percentage"] else away
            winner_team["match_vs"] = away["name"] if winner_team == home else home["name"]
            winner_team["match_date"] = winner_match["date"]
        
        # Underdog: Select a team at random
        if upcoming:
            random_match = random.choice(upcoming)
            teams = [random_match["home_team"], random_match["away_team"]]
            underdog_team = random.choice(teams)
            underdog_team["match_vs"] = random_match["away_team"]["name"] if underdog_team == random_match["home_team"] else random_match["home_team"]["name"]
            underdog_team["match_date"] = random_match["date"]

    return render_template('index.html', matches=upcoming, winner=winner_team, underdog=underdog_team)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)