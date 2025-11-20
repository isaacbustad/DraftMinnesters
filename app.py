from flask import Flask, jsonify, request, render_template
import sqlite3
import subprocess
import json
import requests
import logging
import os
from routes.matches import matches_bp, get_match_data_internal
from routes.user import user_bp
from routes.admin import admin_bp
import random

app = Flask(__name__)
app.register_blueprint(matches_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

# Create logs directory if it doesn't exist
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler(os.path.join(log_dir, 'app.log')), logging.StreamHandler()])

def init_db():
    db_file = 'draft_ministers.db'
    
    try:
        conn = sqlite3.connect(db_file)
        logging.info("Database connected successfully.")
        # Create tables if they don't exist
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_teams (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                code TEXT,
                country TEXT,
                founded INTEGER,
                national INTEGER,
                logo TEXT,
                venue_id INTEGER,
                venue_name TEXT,
                venue_address TEXT,
                venue_city TEXT,
                venue_capacity INTEGER,
                venue_surface TEXT,
                venue_image TEXT,
                league TEXT,
                dmr REAL
            )
        """)
        # Add dmr column to existing tables if it doesn't exist
        try:
            cursor.execute("ALTER TABLE soccer_teams ADD COLUMN dmr REAL")
        except sqlite3.OperationalError:
            # Column already exists, ignore
            pass
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                position TEXT,
                team_id INTEGER,
                age INTEGER,
                FOREIGN KEY (team_id) REFERENCES soccer_teams(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_fixtures (
                fixture_id INTEGER PRIMARY KEY,
                date TEXT,
                timestamp INTEGER,
                status_long TEXT,
                status_short TEXT,
                home_team_id INTEGER,
                away_team_id INTEGER,
                league_id INTEGER,
                league_name TEXT,
                season INTEGER,
                round TEXT,
                venue_id INTEGER,
                venue_name TEXT,
                venue_city TEXT,
                referee TEXT,
                home_goals INTEGER,
                away_goals INTEGER,
                home_winner INTEGER,
                away_winner INTEGER,
                raw_data TEXT,
                home_win_percentage REAL,
                away_win_percentage REAL,
                draw_percentage REAL
            )
        """)
        # Add win percentage columns to existing tables if they don't exist
        for col in ['home_win_percentage', 'away_win_percentage', 'draw_percentage']:
            try:
                cursor.execute(f"ALTER TABLE soccer_fixtures ADD COLUMN {col} REAL")
            except sqlite3.OperationalError:
                # Column already exists, ignore
                pass
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_time TEXT NOT NULL,
                status TEXT,
                teams_updated INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        # Set default cutoff date to 2023-12-31 if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO app_config (key, value) 
            VALUES ('upcoming_match_cutoff_date', '2023-12-31')
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Database connection error: {e}")
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