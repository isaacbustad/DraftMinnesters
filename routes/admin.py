from flask import Blueprint, render_template, jsonify, request
import sqlite3
import logging
import threading
import time
from datetime import datetime
import sys
import os

# Import machine learning module
import importlib.util
ml_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'machine_learning', 'machine_learning.py')
spec = importlib.util.spec_from_file_location("machine_learning", ml_file_path)
ml_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ml_module)
get_all_team_dmrs = ml_module.get_all_team_dmrs

admin_bp = Blueprint('admin', __name__)

DB_FILE = 'draft_ministers.db'

def calculate_win_percentages(home_dmr: float, away_dmr: float) -> tuple:
    """
    Calculate win percentages based on DMR values.
    
    Args:
        home_dmr: DMR rating of home team (defaults to 40 if None - slightly below average)
        away_dmr: DMR rating of away team (defaults to 40 if None - slightly below average)
    
    Returns:
        Tuple of (home_win_percentage, away_win_percentage, draw_percentage)
    """
    # Use 40 as default if DMR is missing (slightly below average DMR of ~42.6)
    if home_dmr is None:
        home_dmr = 40.0
    if away_dmr is None:
        away_dmr = 40.0
    
    # Calculate DMR difference
    dmr_diff = abs(home_dmr - away_dmr)
    
    # Base win probabilities based on DMR ratio
    total_dmr = home_dmr + away_dmr
    if total_dmr == 0:
        home_win_base = 0.33
        away_win_base = 0.33
    else:
        home_win_base = home_dmr / total_dmr
        away_win_base = away_dmr / total_dmr
    
    # Calculate draw probability - higher when DMRs are similar
    # If DMR difference is small (< 5), increase draw probability
    if dmr_diff < 5:
        draw_base = 0.30 - (dmr_diff * 0.02)  # 30% down to 20% based on difference
    elif dmr_diff < 10:
        draw_base = 0.20 - ((dmr_diff - 5) * 0.02)  # 20% down to 10%
    else:
        draw_base = 0.10 - min((dmr_diff - 10) * 0.01, 0.05)  # 10% down to 5%
    
    draw_base = max(0.05, min(0.30, draw_base))  # Clamp between 5% and 30%
    
    # Adjust win probabilities to account for draw
    remaining_prob = 1.0 - draw_base
    home_win = home_win_base * remaining_prob
    away_win = away_win_base * remaining_prob
    
    # Normalize to ensure they sum to 100%
    total = home_win + away_win + draw_base
    home_win = (home_win / total) * 100
    away_win = (away_win / total) * 100
    draw = (draw_base / total) * 100
    
    return round(home_win, 1), round(away_win, 1), round(draw, 1)

# Global state for ML run progress
ml_run_state = {
    'running': False,
    'progress': 0,
    'current_step': '',
    'log': [],
    'teams_updated': 0
}

def get_last_ml_run_time():
    """Get the last ML run time from database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT run_time FROM ml_run_history ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logging.error(f"Error getting last ML run time: {e}")
        return None

@admin_bp.route('/admin')
def admin():
    """Display admin page for administrators with teams from database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM soccer_teams ORDER BY name")
        rows = cursor.fetchall()
        
        teams = []
        for row in rows:
            # Get DMR rating, default to None if column doesn't exist
            try:
                dmr = row['dmr']
            except (KeyError, IndexError):
                dmr = None
            
            teams.append({
                'id': row['id'],
                'name': row['name'],
                'code': row['code'],
                'country': row['country'],
                'founded': row['founded'],
                'national': bool(row['national']),
                'logo': row['logo'],
                'venue_name': row['venue_name'],
                'venue_city': row['venue_city'],
                'venue_capacity': row['venue_capacity'],
                'league': row['league'],
                'dmr': dmr
            })
        
        last_run_time = get_last_ml_run_time()
        
        cursor.close()
        conn.close()
        
        logging.info(f"Loaded {len(teams)} teams for admin page")
        
        return render_template('admin.html', teams=teams, last_run_time=last_run_time)
    except Exception as e:
        logging.error(f"Error loading teams for admin page: {e}")
        return render_template('admin.html', teams=[], error=str(e), last_run_time=None)

def add_log(message):
    """Add a log message to the ML run state."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    ml_run_state['log'].append(log_entry)
    # Keep only last 100 log entries
    if len(ml_run_state['log']) > 100:
        ml_run_state['log'] = ml_run_state['log'][-100:]

def run_ml_process():
    """Run the ML process and update DMRs in the database."""
    global ml_run_state
    
    try:
        ml_run_state['running'] = True
        ml_run_state['progress'] = 0
        ml_run_state['current_step'] = 'Initializing...'
        ml_run_state['log'] = []
        ml_run_state['teams_updated'] = 0
        
        add_log("Starting DMR calculation process...")
        ml_run_state['progress'] = 5
        ml_run_state['current_step'] = 'Importing data'
        add_log("Importing data from databases...")
        time.sleep(0.5)  # Simulate processing time
        
        ml_run_state['progress'] = 15
        ml_run_state['current_step'] = 'Filtering data'
        add_log("Filtering matches for draft teams...")
        time.sleep(0.5)
        
        ml_run_state['progress'] = 30
        ml_run_state['current_step'] = 'Scaling data'
        add_log("Scaling features for model input...")
        time.sleep(0.5)
        
        ml_run_state['progress'] = 50
        ml_run_state['current_step'] = 'Running model with parameters'
        add_log("Running Logistic Regression classifier...")
        add_log("Parameters: multi_class='multinomial', solver='lbfgs', max_iter=1000")
        time.sleep(1)
        
        add_log("Running Linear Regression for goal difference prediction...")
        time.sleep(1)
        
        ml_run_state['progress'] = 70
        ml_run_state['current_step'] = 'Calculating DMR ratings'
        add_log("Calculating DMR ratings for all teams...")
        
        # Actually run the ML function
        team_dmrs = get_all_team_dmrs()
        
        ml_run_state['progress'] = 85
        ml_run_state['current_step'] = 'Updating database'
        add_log(f"Updating database with DMR ratings for {len(team_dmrs)} teams...")
        
        # Update database with DMR values
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        teams_updated = 0
        for team_name, dmr_data in team_dmrs.items():
            # Use recent_dmr if available, otherwise avg_dmr
            dmr_value = dmr_data.get('recent_dmr', dmr_data.get('avg_dmr'))
            
            # Try to match team by name (case-insensitive)
            cursor.execute("""
                UPDATE soccer_teams 
                SET dmr = ? 
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
            """, (dmr_value, team_name))
            
            if cursor.rowcount > 0:
                teams_updated += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        ml_run_state['teams_updated'] = teams_updated
        add_log(f"Successfully updated {teams_updated} teams with DMR ratings")
        
        # Update win percentages for all fixtures
        ml_run_state['progress'] = 90
        ml_run_state['current_step'] = 'Calculating win percentages'
        add_log("Calculating win percentages for fixtures based on DMR ratings...")
        
        # Open new connection for fixtures update
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get all fixtures
        cursor.execute("""
            SELECT fixture_id, home_team_id, away_team_id 
            FROM soccer_fixtures
        """)
        fixtures = cursor.fetchall()
        
        fixtures_updated = 0
        for fixture in fixtures:
            fixture_id, home_team_id, away_team_id = fixture
            
            # Get DMR for home and away teams
            cursor.execute("SELECT dmr FROM soccer_teams WHERE id = ?", (home_team_id,))
            home_dmr_row = cursor.fetchone()
            home_dmr = home_dmr_row[0] if home_dmr_row else None
            
            cursor.execute("SELECT dmr FROM soccer_teams WHERE id = ?", (away_team_id,))
            away_dmr_row = cursor.fetchone()
            away_dmr = away_dmr_row[0] if away_dmr_row else None
            
            # Calculate win percentages
            home_win, away_win, draw = calculate_win_percentages(home_dmr, away_dmr)
            
            # Update fixture with win percentages
            cursor.execute("""
                UPDATE soccer_fixtures 
                SET home_win_percentage = ?, away_win_percentage = ?, draw_percentage = ?
                WHERE fixture_id = ?
            """, (home_win, away_win, draw, fixture_id))
            
            fixtures_updated += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        add_log(f"Successfully updated win percentages for {fixtures_updated} fixtures")
        
        # Record run time
        run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ml_run_history (run_time, status, teams_updated)
            VALUES (?, ?, ?)
        """, (run_time, 'completed', teams_updated))
        conn.commit()
        cursor.close()
        conn.close()
        
        ml_run_state['progress'] = 100
        ml_run_state['current_step'] = 'Completed'
        add_log("DMR calculation process completed successfully!")
        
    except Exception as e:
        error_msg = f"Error during ML process: {str(e)}"
        logging.error(error_msg)
        add_log(error_msg)
        ml_run_state['current_step'] = 'Error'
        
        # Record failed run
        run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ml_run_history (run_time, status, teams_updated)
                VALUES (?, ?, ?)
            """, (run_time, 'failed', 0))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass
    finally:
        ml_run_state['running'] = False

@admin_bp.route('/api/ml/run', methods=['POST'])
def run_ml():
    """Start the ML process in a background thread."""
    global ml_run_state
    
    if ml_run_state['running']:
        return jsonify({'error': 'ML process is already running'}), 400
    
    # Start ML process in background thread
    thread = threading.Thread(target=run_ml_process, daemon=True)
    thread.start()
    
    return jsonify({'status': 'started', 'message': 'ML process started'})

@admin_bp.route('/api/ml/status', methods=['GET'])
def ml_status():
    """Get the current status of the ML process."""
    return jsonify({
        'running': ml_run_state['running'],
        'progress': ml_run_state['progress'],
        'current_step': ml_run_state['current_step'],
        'log': ml_run_state['log'],
        'teams_updated': ml_run_state['teams_updated']
    })

@admin_bp.route('/api/admin/cutoff-date', methods=['GET'])
def get_cutoff_date():
    """Get the current cutoff date for upcoming matches."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_config WHERE key = 'upcoming_match_cutoff_date'")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        cutoff_date = result[0] if result else '2023-12-31'
        return jsonify({'cutoff_date': cutoff_date})
    except Exception as e:
        logging.error(f"Error getting cutoff date: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/cutoff-date', methods=['POST'])
def set_cutoff_date():
    """Set the cutoff date for upcoming matches."""
    try:
        data = request.get_json()
        cutoff_date = data.get('cutoff_date')
        
        if not cutoff_date:
            return jsonify({'error': 'Cutoff date is required'}), 400
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO app_config (key, value) 
            VALUES ('upcoming_match_cutoff_date', ?)
        """, (cutoff_date,))
        conn.commit()
        cursor.close()
        conn.close()
        
        logging.info(f"Cutoff date updated to: {cutoff_date}")
        return jsonify({'message': 'Cutoff date updated successfully', 'cutoff_date': cutoff_date})
    except Exception as e:
        logging.error(f"Error setting cutoff date: {e}")
        return jsonify({'error': str(e)}), 500

