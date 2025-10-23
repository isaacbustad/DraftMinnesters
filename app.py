from flask import Flask, jsonify, request, render_template_string
import mysql.connector
from kafka import KafkaProducer
import subprocess
import json
import requests
import logging
import os

app = Flask(__name__)

# Create logs directory if it doesn't exist
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler(os.path.join(log_dir, 'app.log')), logging.StreamHandler()])

@app.route('/')
def home():
    logging.info("Accessing home endpoint")
    return jsonify({"message": "Welcome to Draft Ministers App - Soccer Prediction!"})

@app.route('/teams', methods=['GET'])
def get_teams():
    logging.info("Fetching all teams from DB")
    try:
        conn = mysql.connector.connect(host='localhost', user='appuser', password='password', database='draft_ministers_db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soccer_teams")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({
            "teams": [dict(zip(['id', 'name', 'code', 'country', 'founded', 'national', 'logo', 'venue_id', 'venue_name', 'venue_address', 'venue_city', 'venue_capacity', 'venue_surface', 'venue_image', 'league'], row)) for row in results]
        })
    except Exception as e:
        logging.error(f"Error fetching teams from DB: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/fetch_teams', methods=['GET'])
def fetch_teams():
    logging.info("Starting fetch_teams endpoint")
    # Fetch teams from API-Football; optional query params league and season (default Premier League 2023)
    league = request.args.get('league', '39')
    season = request.args.get('season', '2023')
    api_key = '055c98bd6e9dfa6bb3eba8e254adab4e'
    url = f"https://v3.football.api-sports.io/teams?league={league}&season={season}"
    headers = {
        "x-apisports-key": api_key
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
        conn = mysql.connector.connect(host='localhost', user='appuser', password='password', database='draft_ministers_db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_teams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE,
                code VARCHAR(10),
                country VARCHAR(255),
                founded INT,
                national BOOLEAN,
                logo VARCHAR(255),
                venue_id INT,
                venue_name VARCHAR(255),
                venue_address VARCHAR(255),
                venue_city VARCHAR(255),
                venue_capacity INT,
                venue_surface VARCHAR(50),
                venue_image VARCHAR(255),
                league VARCHAR(255)
            )
        """)

        for item in teams:
            team = item.get('team', {})
            venue = item.get('venue', {})
            name = team.get('name', 'Unknown')
            code = team.get('code', 'Unknown')
            country = team.get('country', 'Unknown')
            founded = team.get('founded')
            national = team.get('national', False)
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
                cursor.execute("INSERT IGNORE INTO soccer_teams (name, code, country, founded, national, logo, venue_id, venue_name, venue_address, venue_city, venue_capacity, venue_surface, venue_image, league) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
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
        logging.error(f"Error connecting to MySQL: {str(e)}")
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

@app.route('/team', methods=['POST'])
def insert_team():
    logging.info("Starting insert_team endpoint")
    # Expect JSON payload: {"name": "Team A", "country": "USA", "league": "MLS"}
    data = request.json
    if not data or not all(key in data for key in ['name', 'country', 'league']):
        return jsonify({"error": "Missing required fields: name, country, league"}), 400

    try:
        conn = mysql.connector.connect(host='localhost', user='appuser', password='password', database='draft_ministers_db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_teams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE,
                code VARCHAR(10),
                country VARCHAR(255),
                founded INT,
                national BOOLEAN,
                logo VARCHAR(255),
                venue_id INT,
                venue_name VARCHAR(255),
                venue_address VARCHAR(255),
                venue_city VARCHAR(255),
                venue_capacity INT,
                venue_surface VARCHAR(50),
                venue_image VARCHAR(255),
                league VARCHAR(255)
            )
        """)
        cursor.execute("INSERT INTO soccer_teams (name, country, league) VALUES (%s, %s, %s)", 
                       (data['name'], data['country'], data['league']))
        conn.commit()
        team_id = cursor.lastrowid
        cursor.execute("SELECT * FROM soccer_teams WHERE id = %s", (team_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.IntegrityError:
        logging.error("Team name already exists")
        return jsonify({"error": "Team name already exists"}), 400
    except Exception as e:
        logging.error(f"Error inserting team to DB: {str(e)}")
        return jsonify({"error": "Database error"}), 500

    try:
        producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send('team-events', {'event': 'Team inserted', 'team': data['name']})
        producer.flush()
        logging.info("Kafka event sent successfully")
    except Exception as e:
        logging.error(f"Error sending to Kafka: {str(e)}")
        return jsonify({"error": "Kafka error", "details": str(e)}), 500

    try:
        hadoop_output = subprocess.check_output(['hdfs', 'dfs', '-ls', '/team_logs']).decode()
    except:
        hadoop_output = "Hadoop setup in progress..."

    return jsonify({
        "team": dict(zip(['id', 'name', 'code', 'country', 'founded', 'national', 'logo', 'venue_id', 'venue_name', 'venue_address', 'venue_city', 'venue_capacity', 'venue_surface', 'venue_image', 'league'], result)),
        "kafka_status": "Message sent",
        "hadoop_files": hadoop_output
    })

@app.route('/player', methods=['POST'])
def insert_player():
    logging.info("Starting insert_player endpoint")
    # Expect JSON payload: {"name": "John Doe", "position": "Forward", "team_id": 1, "age": 25}
    data = request.json
    if not data or not all(key in data for key in ['name', 'position', 'team_id', 'age']):
        return jsonify({"error": "Missing required fields: name, position, team_id, age"}), 400

    try:
        conn = mysql.connector.connect(host='localhost', user='appuser', password='password', database='draft_ministers_db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soccer_players (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                position VARCHAR(255),
                team_id INT,
                age INT,
                FOREIGN KEY (team_id) REFERENCES soccer_teams(id)
            )
        """)
        cursor.execute("INSERT INTO soccer_players (name, position, team_id, age) VALUES (%s, %s, %s, %s)", 
                       (data['name'], data['position'], data['team_id'], data['age']))
        conn.commit()
        player_id = cursor.lastrowid
        cursor.execute("SELECT * FROM soccer_players WHERE id = %s", (player_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.IntegrityError:
        logging.error("Invalid team_id or duplicate entry")
        return jsonify({"error": "Invalid team_id or duplicate entry"}), 400
    except Exception as e:
        logging.error(f"Error inserting player to DB: {str(e)}")
        return jsonify({"error": "Database error"}), 500

    try:
        producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send('player-events', {'event': 'Player inserted', 'player': data['name']})
        producer.flush()
        logging.info("Kafka event sent successfully")
    except Exception as e:
        logging.error(f"Error sending to Kafka: {str(e)}")
        return jsonify({"error": "Kafka error", "details": str(e)}), 500

    try:
        hadoop_output = subprocess.check_output(['hdfs', 'dfs', '-ls', '/player_logs']).decode()
    except:
        hadoop_output = "Hadoop setup in progress..."

    return jsonify({
        "player": dict(zip(['id', 'name', 'position', 'team_id', 'age'], result)),
        "kafka_status": "Message sent",
        "hadoop_files": hadoop_output
    })

@app.route('/team_details/<int:team_id>', methods=['GET'])
def team_details(team_id):
    logging.info(f"Fetching details for team ID {team_id}")
    try:
        conn = mysql.connector.connect(host='localhost', user='appuser', password='password', database='draft_ministers_db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soccer_teams WHERE id = %s", (team_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            logging.error(f"Team ID {team_id} not found")
            return jsonify({"error": "Team not found"}), 404

        team = dict(zip(['id', 'name', 'code', 'country', 'founded', 'national', 'logo', 'venue_id', 'venue_name', 'venue_address', 'venue_city', 'venue_capacity', 'venue_surface', 'venue_image', 'league'], result))

        # Render HTML with team details and logo
        html = """
        <html>
        <body>
            <h1>Team Details</h1>
            <p>ID: {{ team.id }}</p>
            <p>Name: {{ team.name }}</p>
            <p>Code: {{ team.code }}</p>
            <p>Country: {{ team.country }}</p>
            <p>Founded: {{ team.founded }}</p>
            <p>National: {{ team.national }}</p>
            <img src="{{ team.logo }}" alt="{{ team.name }} logo" width="200">
            <h2>Venue Details</h2>
            <p>Venue ID: {{ team.venue_id }}</p>
            <p>Venue Name: {{ team.venue_name }}</p>
            <p>Address: {{ team.venue_address }}</p>
            <p>City: {{ team.venue_city }}</p>
            <p>Capacity: {{ team.venue_capacity }}</p>
            <p>Surface: {{ team.venue_surface }}</p>
            <img src="{{ team.venue_image }}" alt="{{ team.venue_name }} image" width="200">
            <button onclick="window.location.href='/fetch_teams';">Fetch Teams</button>
        </body>
        </html>
        """
        return render_template_string(html, team=team)
    except Exception as e:
        logging.error(f"Error fetching team details for ID {team_id}: {str(e)}")
        return jsonify({"error": "Database error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)