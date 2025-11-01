# We need to refactor this code , this code below used to belong to the app.py however we do not want to have SQL queries in Flask directly..
# Placeholder currently. 

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

@app.route('/teams', methods=['GET'])
def get_teams():
    logging.info("Fetching all teams from DB")
    try:
        conn = sqlite3.connect('draft_ministers.db')
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
    url = f"https://v3.football.api-sports.io/teams?league={league}&season={season}"
    headers = {
        "x-apisports-key": secret.secret()
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

@app.route('/team', methods=['POST'])
def insert_team():
    logging.info("Starting insert_team endpoint")
    # Expect JSON payload: {"name": "Team A", "country": "USA", "league": "MLS"}
    data = request.json
    if not data or not all(key in data for key in ['name', 'country', 'league']):
        return jsonify({"error": "Missing required fields: name, country, league"}), 400

    try:
        conn = sqlite3.connect('draft_ministers.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO soccer_teams (name, country, league) VALUES (?, ?, ?)", 
                       (data['name'], data['country'], data['league']))
        conn.commit()
        team_id = cursor.lastrowid
        cursor.execute("SELECT * FROM soccer_teams WHERE id = ?", (team_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
    except sqlite3.IntegrityError:
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
        conn = sqlite3.connect('draft_ministers.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO soccer_players (name, position, team_id, age) VALUES (?, ?, ?, ?)", 
                       (data['name'], data['position'], data['team_id'], data['age']))
        conn.commit()
        player_id = cursor.lastrowid
        cursor.execute("SELECT * FROM soccer_players WHERE id = ?", (player_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
    except sqlite3.IntegrityError:
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
        conn = sqlite3.connect('draft_ministers.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM soccer_teams WHERE id = ?", (team_id,))
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