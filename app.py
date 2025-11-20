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
        <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
        <script src="{{ url_for('static', filename='js/nav.js') }}"></script>
    </head>
    <body>
        <header>
            <h1>Welcome to Draft Ministers App - Soccer Prediction!</h1>
            <p>Follow us on <a href="#" style="color: #1DA1F2;">Twitter</a> and <a href="#" style="color: #1DA1F2;">Facebook</a></p>
        </header>
        <main>
            <img src="{{ url_for('static', filename='images/soccer_banner.jpg') }}" alt="Most Likely to Win" style="width:auto; height:auto; ">
            <div class="banner-container">Underdogs</div>
            <div class="banner-container">Upcoming Matches</div>
            <div class="banner-container">Most Likely to Win</div>
            <nav class="navigation">
                <button role="tab" class="nav-links active" onclick="toggleNav(event, 'upcoming-matches-container')" aria-selected="true">Upcoming Matches</button>
                <button role="tab" class="nav-links" onclick="toggleNav(event, 'most-likely-to-win-container')">Most Likely to Win</button>
                <button role="tab" class="nav-links" onclick="toggleNav(event, 'most-likely-to-lose-container')">Most Likely to Lose</button>
                <button role="tab" class="nav-links" onclick="toggleNav(event, 'starred-container')">Starred</button>
            </nav>
            <div id="upcoming-matches-container" class="nav-content" style="display: block;" aria-labelledby="tab-upcoming">
                <h2>Welcome to the Draft Ministers App</h2>
                <p>Your one-stop solution for soccer match predictions.</p>
            </div>
            <div id="most-likely-to-win-container" class="nav-content" aria-labelledby="tab-most-likely">
                <h2>Most Likely to Win</h2>
                <p>Discover the teams with the highest chances of winning their upcoming matches.</p>
            </div>
            <div id="most-likely-to-lose-container" class="nav-content" aria-labelledby="tab-least-likely">
                <h2>Most Likely to Lose</h2>
                <p>Find out which teams are predicted to face tough challenges in their next games.</p>
            </div>
            <div id="starred-container" class="nav-content" aria-labelledby="tab-starred">
                <h2>Starred Players</h2>
                <p>Highlighting the standout players to watch in the upcoming matches.</p>
            </div>
        </main>
        <footer>
            <p>&copy; 2025 Draft Ministers</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(html)

def kafka():
    league = request.args.get('league', '39')
    season = request.args.get('season', '2023')
    url = f"https://v3.football.api-sports.io/teams?league={league}&season={season}"
    headers = {
        "x-apisports-key": secret.API_SPORTS_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        logging.debug(f"API response status: {response.status_code}")
        if response.status_code != 200:
            logging.error(f"API fetch failed with status {response.status_code}")
            return jsonify({"error": "Failed to fetch teams from API", "status": response.status_code}), response.status_code

        data = response.json()
        teams = data.get('response', [])
    except Exception as e:
        logging.error(f"Error fetching API: {str(e)}")
        return jsonify({"error": "API fetch error"}), 500

    inserted_teams = []
    try:
        conn = sqlite3.connect('draft_ministers.db')
        cursor = conn.cursor()

        for item in teams:
            team = item.get('team', {})
            venue = item.get('venue', {})
            name = team.get('name', 'Unknown')
            code = team.get('code', 'Unknown')
            country = team.get('country', 'Unknown')
            founded = team.get('founded')
            national = 1 if team.get('national', False) else 0
            logo = team.get('logo')
            venue_id = venue.get('id')
            venue_name = venue.get('name')
            venue_address = venue.get('address')
            venue_city = venue.get('city')
            venue_capacity = venue.get('capacity')
            venue_surface = venue.get('surface')
            venue_image = venue.get('image')
            league_name = 'Unknown'  # League is from param, but can fetch if needed

            try:
                cursor.execute("INSERT OR IGNORE INTO soccer_teams (name, code, country, founded, national, logo, venue_id, venue_name, venue_address, venue_city, venue_capacity, venue_surface, venue_image, league) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                               (name, code, country, founded, national, logo, venue_id, venue_name, venue_address, venue_city, venue_capacity, venue_surface, venue_image, league_name))
                conn.commit()
                if cursor.rowcount > 0:
                    inserted_teams.append(name)
            except Exception as e:
                logging.error(f"Error inserting team {name}: {str(e)}")
                pass  # Skip errors (e.g., duplicates)

        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error connecting to SQLite: {str(e)}")
        return jsonify({"error": "Database error"}), 500

    try:
        producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send('team-events', {'event': 'Teams fetched from API', 'count': len(inserted_teams)})
        producer.flush()
        logging.info("Kafka event sent successfully")
    except Exception as e:
        logging.error(f"Error sending to Kafka: {str(e)}")
        return jsonify({"error": "Kafka error", "details": str(e)}), 500

    return jsonify({
        "inserted_teams": inserted_teams,
        "kafka_status": "Message sent"
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)