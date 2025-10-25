from flask import Flask, jsonify, request, render_template_string
import sqlite3
from kafka import KafkaProducer
import subprocess
import json
import requests
import logging
import os
from routes.predict import predict_bp
import secret_tunnel as secret

app = Flask(__name__)
app.register_blueprint(predict_bp)

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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                league TEXT
            )
        """)
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
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise e

@app.route('/')
def home():
    logging.info("Accessing home endpoint")
    html = """
    <html>
    <head>
        <title>Draft Ministers App - Soccer Prediction</title>
        <link rel="stylesheet" type="text/css" href="/static/styles.css">
    </head>
    <body>
        <header>
            <h1>Welcome to Draft Ministers App - Soccer Prediction!</h1>
            <p>Follow us on <a href="#" style="color: #1DA1F2;">Twitter</a> and <a href="#" style="color: #1DA1F2;">Facebook</a></p>
        </header>
        <main>
            <nav>
                <ul class="nav-links">
                    <li><a href="/predict">Upcoming Matches</a></li>
                    <li><a href="/docs">Most Likely to Win</a></li>
                    <li><a href="/stats">Most Likely to Lose</a></li>
                    <li><a href="/about">Starred</a></li>
                </ul>
            </nav>
        </main>
        <footer>
            <p>&copy; 2025 Draft Ministers</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)