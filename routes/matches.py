from flask import Blueprint, jsonify
import requests
import random
from datetime import datetime
import logging
import sqlite3
import json
import os
from routes.admin import calculate_win_percentages

matches_bp = Blueprint('matches', __name__)

API_BASE_URL = "https://v3.football.api-sports.io"
API_KEY = "13298635a1431cb71e482ddd48f70ce8"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

DB_FILE = 'draft_ministers.db'

def fetch_teams() -> dict:
    """Load teams from local JSON file for MVP demo."""
    try:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'json_response', 'teams_response.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading teams from JSON: {e}")
        return None

def fetch_fixtures() -> dict:
    """Load fixtures from local JSON file for MVP demo."""
    try:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'json_response', 'fixtures_response.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading fixtures from JSON: {e}")
        return None

def generate_win_percentages():
    """Generate random win percentages for home, away, and draw."""
    home_win = random.uniform(0.20, 0.75)
    away_win = random.uniform(0.15, 0.70)
    draw = random.uniform(0.10, 0.25)
    
    # Normalize to sum to 100%
    total = home_win + away_win + draw
    home_win = round((home_win / total) * 100, 1)
    away_win = round((away_win / total) * 100, 1)
    draw = round((draw / total) * 100, 1)
    
    return home_win, away_win, draw

def clear_database():
    """Clear all teams and fixtures from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM soccer_fixtures")
        cursor.execute("DELETE FROM soccer_teams")
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Database cleared successfully")
        return True
    except Exception as e:
        logging.error(f"Error clearing database: {e}")
        return False

def save_teams_to_db(teams_data: dict) -> bool:
    """Save teams data to the database."""
    if not teams_data or "response" not in teams_data:
        return False
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        for item in teams_data.get("response", []):
            team = item.get("team", {})
            venue = item.get("venue", {})
            
            cursor.execute("""
                INSERT OR REPLACE INTO soccer_teams 
                (id, name, code, country, founded, national, logo, venue_id, venue_name, 
                 venue_address, venue_city, venue_capacity, venue_surface, venue_image, league, dmr)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                team.get("id"),
                team.get("name", ""),
                team.get("code", ""),
                team.get("country", ""),
                team.get("founded"),
                1 if team.get("national", False) else 0,
                team.get("logo", ""),
                venue.get("id"),
                venue.get("name", ""),
                venue.get("address", ""),
                venue.get("city", ""),
                venue.get("capacity"),
                venue.get("surface", ""),
                venue.get("image", ""),
                "Premier League",
                None  # DMR rating - to be set separately
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Teams saved to database successfully")
        return True
    except Exception as e:
        logging.error(f"Error saving teams to database: {e}")
        return False

def save_fixtures_to_db(fixtures_data: dict) -> bool:
    """Save fixtures data to the database."""
    if not fixtures_data or "response" not in fixtures_data:
        return False
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        for item in fixtures_data.get("response", []):
            fixture = item.get("fixture", {})
            teams = item.get("teams", {})
            league = item.get("league", {})
            goals = item.get("goals", {})
            venue = fixture.get("venue", {})
            status = fixture.get("status", {})
            
            cursor.execute("""
                INSERT OR REPLACE INTO soccer_fixtures 
                (fixture_id, date, timestamp, status_long, status_short, home_team_id, away_team_id,
                 league_id, league_name, season, round, venue_id, venue_name, venue_city, referee,
                 home_goals, away_goals, home_winner, away_winner, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fixture.get("id"),
                fixture.get("date", ""),
                fixture.get("timestamp"),
                status.get("long", ""),
                status.get("short", ""),
                teams.get("home", {}).get("id"),
                teams.get("away", {}).get("id"),
                league.get("id"),
                league.get("name", ""),
                league.get("season"),
                league.get("round", ""),
                venue.get("id"),
                venue.get("name", ""),
                venue.get("city", ""),
                fixture.get("referee", ""),
                goals.get("home"),
                goals.get("away"),
                1 if teams.get("home", {}).get("winner") else 0,
                1 if teams.get("away", {}).get("winner") else 0,
                json.dumps(item)
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Fixtures saved to database successfully")
        return True
    except Exception as e:
        logging.error(f"Error saving fixtures to database: {e}")
        return False

def load_teams_from_db() -> dict:
    """Load teams from the database and return in API format."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM soccer_teams")
        rows = cursor.fetchall()
        
        if not rows:
            cursor.close()
            conn.close()
            return None
        
        response = []
        for row in rows:
            response.append({
                "team": {
                    "id": row["id"],
                    "name": row["name"],
                    "code": row["code"],
                    "country": row["country"],
                    "founded": row["founded"],
                    "national": bool(row["national"]),
                    "logo": row["logo"]
                },
                "venue": {
                    "id": row["venue_id"],
                    "name": row["venue_name"],
                    "address": row["venue_address"],
                    "city": row["venue_city"],
                    "capacity": row["venue_capacity"],
                    "surface": row["venue_surface"],
                    "image": row["venue_image"]
                }
            })
        
        cursor.close()
        conn.close()
        logging.info(f"Loaded {len(response)} teams from database")
        return {"response": response}
    except Exception as e:
        logging.error(f"Error loading teams from database: {e}")
        return None

def load_fixtures_from_db() -> dict:
    """Load fixtures from the database and return in API format."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM soccer_fixtures")
        rows = cursor.fetchall()
        
        if not rows:
            cursor.close()
            conn.close()
            return None
        
        response = []
        for row in rows:
            raw_data = json.loads(row["raw_data"]) if row["raw_data"] else {}
            response.append((raw_data if raw_data else {
                "fixture": {
                    "id": row["fixture_id"],
                    "date": row["date"],
                    "timestamp": row["timestamp"],
                    "referee": row["referee"],
                    "status": {
                        "long": row["status_long"],
                        "short": row["status_short"]
                    },
                    "venue": {
                        "id": row["venue_id"],
                        "name": row["venue_name"],
                        "city": row["venue_city"]
                    }
                },
                "teams": {
                    "home": {"id": row["home_team_id"]},
                    "away": {"id": row["away_team_id"]}
                },
                "league": {
                    "id": row["league_id"],
                    "name": row["league_name"],
                    "season": row["season"],
                    "round": row["round"]
                },
                "goals": {
                    "home": row["home_goals"],
                    "away": row["away_goals"]
                }
            }, dict(row)))
        
        cursor.close()
        conn.close()
        logging.info(f"Loaded {len(response)} fixtures from database")
        return {"response": response}
    except Exception as e:
        logging.error(f"Error loading fixtures from database: {e}")
        return None

def format_match_data(fixture: dict, teams_map: dict, fixture_row: dict = None, cutoff_date: str = None) -> dict:
    """Format fixture data for frontend display."""
    fixture_data = fixture.get("fixture", {})
    teams_data = fixture.get("teams", {})
    home_team = teams_data.get("home", {})
    away_team = teams_data.get("away", {})
    
    # Get team IDs once
    home_team_id = home_team.get("id")
    away_team_id = away_team.get("id")
    
    # Try to get win percentages from database first
    if fixture_row:
        try:
            home_win = fixture_row.get("home_win_percentage")
            away_win = fixture_row.get("away_win_percentage")
            draw = fixture_row.get("draw_percentage")
            
            # If percentages exist in database, use them
            if home_win is not None and away_win is not None and draw is not None:
                home_win = float(home_win)
                away_win = float(away_win)
                draw = float(draw)
            else:
                # Calculate using DMR if available, otherwise fallback to random
                home_dmr = teams_map.get(home_team_id, {}).get("dmr")
                away_dmr = teams_map.get(away_team_id, {}).get("dmr")
                
                if home_dmr is not None or away_dmr is not None:
                    # Use DMR-based calculation
                    home_win, away_win, draw = calculate_win_percentages(home_dmr, away_dmr)
                else:
                    # Fallback to random if DMR not available
                    home_win, away_win, draw = generate_win_percentages()
        except (KeyError, ValueError, TypeError):
            # Calculate using DMR if available, otherwise fallback to random
            home_dmr = teams_map.get(home_team_id, {}).get("dmr")
            away_dmr = teams_map.get(away_team_id, {}).get("dmr")
            
            if home_dmr is not None or away_dmr is not None:
                # Use DMR-based calculation
                home_win, away_win, draw = calculate_win_percentages(home_dmr, away_dmr)
            else:
                # Fallback to random if DMR not available
                home_win, away_win, draw = generate_win_percentages()
    else:
        # No database row provided, calculate using DMR if available
        home_dmr = teams_map.get(home_team_id, {}).get("dmr")
        away_dmr = teams_map.get(away_team_id, {}).get("dmr")
        
        if home_dmr is not None or away_dmr is not None:
            # Use DMR-based calculation
            home_win, away_win, draw = calculate_win_percentages(home_dmr, away_dmr)
        else:
            # Fallback to random if DMR not available
            home_win, away_win, draw = generate_win_percentages()
    
    # Get team logos from teams_map
    home_logo = teams_map.get(home_team_id, {}).get("logo", "")
    away_logo = teams_map.get(away_team_id, {}).get("logo", "")
    
    # Format date
    date_str = fixture_data.get("date", "")
    match_date = None
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace("+00:00", ""))
            match_date = dt.strftime("%Y-%m-%d %H:%M")
        except:
            match_date = date_str
    
    status = fixture_data.get("status", {})
    status_long = status.get("long", "")
    
    # Determine if match is past or upcoming based on cutoff date
    # Use current date if cutoff_date is empty
    is_upcoming = True
    match_status = "upcoming"
    
    if date_str:
        try:
            match_dt = datetime.fromisoformat(date_str.replace("+00:00", ""))
            match_date_obj = match_dt.date()
            
            # Use cutoff date if provided, otherwise use current date
            if cutoff_date:
                try:
                    cutoff_dt = datetime.strptime(cutoff_date, "%Y-%m-%d")
                    reference_date = cutoff_dt.date()
                    logging.debug(f"Using cutoff date: {reference_date} (from {cutoff_date})")
                except (ValueError, AttributeError) as e:
                    # If cutoff date parsing fails, use current date
                    logging.warning(f"Failed to parse cutoff date '{cutoff_date}': {e}, using current date")
                    reference_date = datetime.now().date()
            else:
                # If no cutoff date set, use current date
                logging.debug("No cutoff date set, using current date")
                reference_date = datetime.now().date()
            
            # Match is past if its date is before the reference date
            # If cutoff is Sep 30, 2023, matches from Aug 2023 should be past
            if match_date_obj < reference_date:
                is_upcoming = False
                match_status = "past match"
                logging.debug(f"Match {fixture_data.get('id')} on {match_date_obj} is PAST (cutoff: {reference_date})")
            else:
                is_upcoming = True
                match_status = "upcoming"
                logging.debug(f"Match {fixture_data.get('id')} on {match_date_obj} is UPCOMING (cutoff: {reference_date})")
        except (ValueError, AttributeError):
            # If date parsing fails, default to upcoming for backward compatibility
            is_upcoming = True
            match_status = "upcoming"
    else:
        # If no date, default to upcoming
        is_upcoming = True
        match_status = "upcoming"
    
    return {
        "id": fixture_data.get("id"),
        "home_team": {
            "id": home_team_id,
            "name": home_team.get("name", ""),
            "code": home_team.get("code", ""),
            "logo": home_logo,
            "win_percentage": home_win
        },
        "away_team": {
            "id": away_team_id,
            "name": away_team.get("name", ""),
            "code": away_team.get("code", ""),
            "logo": away_logo,
            "win_percentage": away_win
        },
        "draw_percentage": draw,
        "date": match_date,
        "status": status_long,
        "is_upcoming": is_upcoming,
        "match_status": match_status
    }

def get_match_data_internal():
    """Internal helper to get match data."""
    # Try to load from database first
    teams_data = load_teams_from_db()
    fixtures_data = load_fixtures_from_db()
    
    # If database is empty, fetch from API and save
    if not teams_data or not fixtures_data:
        logging.info("Database empty, fetching from API")
        teams_data = fetch_teams()
        fixtures_data = fetch_fixtures()
        
        if not teams_data or not fixtures_data:
            return {"error": "Failed to fetch data from API"}
        
        # Save to database for next time
        save_teams_to_db(teams_data)
        save_fixtures_to_db(fixtures_data)
    
    # Get cutoff date from database
    cutoff_date = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_config WHERE key = 'upcoming_match_cutoff_date'")
        result = cursor.fetchone()
        if result and result[0]:
            cutoff_date = result[0].strip()
            # If empty string, treat as None
            if not cutoff_date:
                cutoff_date = None
        cursor.close()
        conn.close()
        if cutoff_date:
            logging.info(f"Retrieved cutoff date from DB: {cutoff_date}")
        else:
            logging.info("No cutoff date found in DB, will use current date")
    except Exception as e:
        logging.error(f"Error getting cutoff date: {e}")
        cutoff_date = None
    
    # Create teams map for quick lookup with DMR values
    teams_map = {}
    # Load DMR values from database
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, dmr FROM soccer_teams")
    dmr_rows = cursor.fetchall()
    dmr_map = {row["id"]: row["dmr"] for row in dmr_rows}
    cursor.close()
    conn.close()
    
    for team_item in teams_data.get("response", []):
        team = team_item.get("team", {})
        team_id = team.get("id")
        teams_map[team_id] = {
            "name": team.get("name", ""),
            "code": team.get("code", ""),
            "logo": team.get("logo", ""),
            "dmr": dmr_map.get(team_id)
        }
    
    # Process fixtures
    fixtures = fixtures_data.get("response", [])
    matches = []
    
    for fixture_item in fixtures:
        # Handle both old format (dict) and new format (tuple of dict, row_dict)
        if isinstance(fixture_item, tuple):
            fixture, fixture_row = fixture_item
        else:
            fixture = fixture_item
            fixture_row = None
        
        match_data = format_match_data(fixture, teams_map, fixture_row, cutoff_date)
        matches.append(match_data)
    
    # Filter matches based on cutoff date - only include matches marked as upcoming
    upcoming_matches = [m for m in matches if m.get("is_upcoming", True)]
    past_matches = [m for m in matches if not m.get("is_upcoming", True)]
    logging.info(f"Total matches: {len(matches)}, Upcoming: {len(upcoming_matches)}, Past: {len(past_matches)}, Cutoff date used: {cutoff_date}")
    
    # Sort by date
    upcoming_matches.sort(key=lambda x: x.get("date", ""))
    
    # Get most likely to win (highest home team win percentage)
    most_likely_to_win = sorted(
        upcoming_matches,
        key=lambda x: x["home_team"]["win_percentage"],
        reverse=True
    )[:10]
    
    # Get most likely to lose (lowest home team win percentage)
    most_likely_to_lose = sorted(
        upcoming_matches,
        key=lambda x: x["home_team"]["win_percentage"]
    )[:10]
    
    return {
        "upcoming": upcoming_matches,  # Show all 2023 fixtures as upcoming
        "most_likely_to_win": most_likely_to_win,
        "most_likely_to_lose": most_likely_to_lose
    }

@matches_bp.route('/api/matches', methods=['GET'])
def get_matches():
    """Fetch and return match data with predictions. Checks database first."""
    data = get_match_data_internal()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data)

@matches_bp.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """Clear database and fetch latest data from API."""
    try:
        # Clear database
        if not clear_database():
            return jsonify({"error": "Failed to clear database"}), 500
        
        # Clear DMR history (ml_run_history table)
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ml_run_history")
            conn.commit()
            cursor.close()
            conn.close()
            logging.info("DMR history cleared successfully")
        except Exception as e:
            logging.error(f"Error clearing DMR history: {e}")
        
        # Fetch fresh data from API
        teams_data = fetch_teams()
        fixtures_data = fetch_fixtures()
        
        if not teams_data or not fixtures_data:
            return jsonify({"error": "Failed to fetch data from API"}), 500
        
        # Save to database
        if not save_teams_to_db(teams_data) or not save_fixtures_to_db(fixtures_data):
            return jsonify({"error": "Failed to save data to database"}), 500
        
        return jsonify({
            "message": "Data refreshed successfully",
            "teams_count": len(teams_data.get("response", [])),
            "fixtures_count": len(fixtures_data.get("response", []))
        })
    except Exception as e:
        logging.error(f"Error refreshing data: {e}")
        return jsonify({"error": str(e)}), 500
