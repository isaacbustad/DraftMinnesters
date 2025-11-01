# Placeholder currently.

def GenerateIndex(team_id):
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

