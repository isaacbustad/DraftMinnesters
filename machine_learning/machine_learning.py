"""
Machine Learning Module for Draft Minnester Rating (DMR)

This module provides functions to calculate and retrieve team DMR ratings
for use in the Flask application.
"""

import pandas as pd
import numpy as np
import sqlite3
import os
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Global variables to store models and data
_models_loaded = False
_final_clf = None
_final_reg = None
_scaler = None
_le = None
_df_team_ratings = None
_df_features = None
_df_team = None
_feature_cols = None


def _load_data_and_models():
    """Load data and train models. Called once on first use."""
    global _models_loaded, _final_clf, _final_reg, _scaler, _le
    global _df_team_ratings, _df_features, _df_team, _feature_cols
    
    if _models_loaded:
        return
    
    # Get paths relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "football_database.sqlite")
    draft_db_path = os.path.join(current_dir, "..", "draft_ministers.db")
    
    # Connect to databases
    connection = sqlite3.connect(db_path)
    conn_draft = sqlite3.connect(draft_db_path)
    
    # Load dataframes
    df_match = pd.read_sql_query("SELECT * FROM Match", connection)
    df_team = pd.read_sql_query("SELECT * FROM Team", connection)
    df_draft_teams = pd.read_sql_query("SELECT * FROM soccer_teams", conn_draft)
    
    # Filter matches to draft teams
    df_team['team_name_normalized'] = df_team['team_long_name'].str.lower().str.strip()
    df_draft_teams['name_normalized'] = df_draft_teams['name'].str.lower().str.strip()
    
    draft_team_ids = df_team[df_team['team_name_normalized'].isin(df_draft_teams['name_normalized'])]['team_api_id'].unique()
    
    df_match_filtered = df_match[
        (df_match['home_team_api_id'].isin(draft_team_ids)) & 
        (df_match['away_team_api_id'].isin(draft_team_ids))
    ].copy()
    
    # Convert dates
    df_match_filtered['date'] = pd.to_datetime(df_match_filtered['date'])
    df_match_filtered = df_match_filtered.sort_values('date').reset_index(drop=True)
    
    # Get match results
    def get_match_result(row):
        home_goals = row.get('home_team_goal', 0)
        away_goals = row.get('away_team_goal', 0)
        if pd.isna(home_goals) or pd.isna(away_goals):
            return None
        if home_goals > away_goals:
            return 'Home Win'
        elif home_goals < away_goals:
            return 'Away Win'
        else:
            return 'Draw'
    
    df_match_filtered['result'] = df_match_filtered.apply(get_match_result, axis=1)
    df_match_filtered['goal_difference'] = df_match_filtered['home_team_goal'] - df_match_filtered['away_team_goal']
    df_match_filtered = df_match_filtered[df_match_filtered['result'].notna()].copy()
    
    # Create features
    df_features = df_match_filtered[['id', 'date', 'home_team_api_id', 'away_team_api_id', 
                                     'result', 'goal_difference', 'home_team_goal', 'away_team_goal']].copy()
    
    df_features['year'] = pd.to_datetime(df_features['date']).dt.year
    df_features['month'] = pd.to_datetime(df_features['date']).dt.month
    df_features['day_of_week'] = pd.to_datetime(df_features['date']).dt.dayofweek
    
    df_features['home_team_id'] = df_features['home_team_api_id'].astype('category').cat.codes
    df_features['away_team_id'] = df_features['away_team_api_id'].astype('category').cat.codes
    
    if 'league_id' in df_match_filtered.columns:
        df_features['league_id'] = df_match_filtered['league_id'].astype('category').cat.codes
    else:
        df_features['league_id'] = 0
    
    # Calculate historical features
    features_list = []
    for idx, match in df_features.iterrows():
        match_date = match['date']
        home_team = match['home_team_api_id']
        away_team = match['away_team_api_id']
        
        home_prev = df_features[
            ((df_features['home_team_api_id'] == home_team) | (df_features['away_team_api_id'] == home_team)) &
            (df_features['date'] < match_date)
        ]
        
        away_prev = df_features[
            ((df_features['home_team_api_id'] == away_team) | (df_features['away_team_api_id'] == away_team)) &
            (df_features['date'] < match_date)
        ]
        
        # Home team stats
        if len(home_prev) > 0:
            home_wins = 0
            home_goals_scored = []
            home_goals_conceded = []
            
            for _, prev_match in home_prev.iterrows():
                is_home = prev_match['home_team_api_id'] == home_team
                h_goals = prev_match['home_team_goal']
                a_goals = prev_match['away_team_goal']
                
                if is_home:
                    home_goals_scored.append(h_goals)
                    home_goals_conceded.append(a_goals)
                    if h_goals > a_goals:
                        home_wins += 1
                else:
                    home_goals_scored.append(a_goals)
                    home_goals_conceded.append(h_goals)
                    if a_goals > h_goals:
                        home_wins += 1
            
            home_win_rate = home_wins / len(home_prev)
            home_avg_goals_scored = np.mean(home_goals_scored) if home_goals_scored else 1.0
            home_avg_goals_conceded = np.mean(home_goals_conceded) if home_goals_conceded else 1.0
        else:
            home_win_rate = 0.33
            home_avg_goals_scored = 1.0
            home_avg_goals_conceded = 1.0
        
        # Away team stats
        if len(away_prev) > 0:
            away_wins = 0
            away_goals_scored = []
            away_goals_conceded = []
            
            for _, prev_match in away_prev.iterrows():
                is_home = prev_match['home_team_api_id'] == away_team
                h_goals = prev_match['home_team_goal']
                a_goals = prev_match['away_team_goal']
                
                if is_home:
                    away_goals_scored.append(h_goals)
                    away_goals_conceded.append(a_goals)
                    if h_goals > a_goals:
                        away_wins += 1
                else:
                    away_goals_scored.append(a_goals)
                    away_goals_conceded.append(h_goals)
                    if a_goals > h_goals:
                        away_wins += 1
            
            away_win_rate = away_wins / len(away_prev)
            away_avg_goals_scored = np.mean(away_goals_scored) if away_goals_scored else 1.0
            away_avg_goals_conceded = np.mean(away_goals_conceded) if away_goals_conceded else 1.0
        else:
            away_win_rate = 0.33
            away_avg_goals_scored = 1.0
            away_avg_goals_conceded = 1.0
        
        match_row = match.copy()
        match_row['home_win_rate'] = home_win_rate
        match_row['home_avg_goals_scored'] = home_avg_goals_scored
        match_row['home_avg_goals_conceded'] = home_avg_goals_conceded
        match_row['away_win_rate'] = away_win_rate
        match_row['away_avg_goals_scored'] = away_avg_goals_scored
        match_row['away_avg_goals_conceded'] = away_avg_goals_conceded
        
        features_list.append(match_row)
    
    df_features = pd.DataFrame(features_list)
    
    # Prepare features and targets
    feature_cols = [
        'home_team_id', 'away_team_id', 
        'year', 'month', 'day_of_week', 'league_id',
        'home_win_rate', 'home_avg_goals_scored', 'home_avg_goals_conceded',
        'away_win_rate', 'away_avg_goals_scored', 'away_avg_goals_conceded'
    ]
    
    X = df_features[feature_cols].copy()
    y_class = df_features['result'].copy()
    y_reg = df_features['goal_difference'].copy()
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_class)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(
        scaler.fit_transform(X),
        columns=X.columns,
        index=X.index
    )
    
    # Train models
    final_clf = LogisticRegression(
        multi_class='multinomial',
        solver='lbfgs',
        max_iter=1000,
        random_state=42
    )
    final_clf.fit(X_scaled, y_encoded)
    
    final_reg = LinearRegression()
    final_reg.fit(X_scaled, y_reg)
    
    # Generate predictions and DMR
    def calculate_dmr(win_prob, draw_prob, loss_prob, goal_diff_pred, recent_form_bonus=0):
        base_rating = (win_prob * 100) + (draw_prob * 33)
        form_bonus = np.clip(recent_form_bonus, -10, 10)
        goal_diff_bonus = np.clip(goal_diff_pred * 5, -15, 15)
        dmr = base_rating + form_bonus + goal_diff_bonus
        return np.clip(dmr, 0, 100)
    
    y_pred_proba_all = final_clf.predict_proba(X_scaled)
    y_pred_reg_all = final_reg.predict(X_scaled)
    
    df_predictions = df_features[['id', 'date', 'home_team_api_id', 'away_team_api_id', 
                                 'result', 'goal_difference']].copy()
    df_predictions.rename(columns={'id': 'match_id'}, inplace=True)
    
    df_predictions['pred_win_prob'] = y_pred_proba_all[:, le.transform(['Home Win'])[0]]
    df_predictions['pred_draw_prob'] = y_pred_proba_all[:, le.transform(['Draw'])[0]]
    df_predictions['pred_loss_prob'] = y_pred_proba_all[:, le.transform(['Away Win'])[0]]
    df_predictions['pred_goal_diff'] = y_pred_reg_all
    
    df_predictions['home_dmr'] = df_predictions.apply(
        lambda row: calculate_dmr(
            row['pred_win_prob'],
            row['pred_draw_prob'],
            row['pred_loss_prob'],
            row['pred_goal_diff'],
            recent_form_bonus=0
        ), axis=1
    )
    
    df_predictions['away_dmr'] = df_predictions.apply(
        lambda row: calculate_dmr(
            row['pred_loss_prob'],
            row['pred_draw_prob'],
            row['pred_win_prob'],
            -row['pred_goal_diff'],
            recent_form_bonus=0
        ), axis=1
    )
    
    # Calculate team ratings
    team_ratings = []
    for team_id in draft_team_ids:
        team_matches = df_predictions[
            (df_predictions['home_team_api_id'] == team_id) | 
            (df_predictions['away_team_api_id'] == team_id)
        ]
        
        if len(team_matches) == 0:
            continue
        
        team_name = df_team[df_team['team_api_id'] == team_id]['team_long_name'].values
        team_name = team_name[0] if len(team_name) > 0 else f"Team {team_id}"
        
        home_matches = team_matches[team_matches['home_team_api_id'] == team_id]
        away_matches = team_matches[team_matches['away_team_api_id'] == team_id]
        
        home_dmrs = home_matches['home_dmr'].values if len(home_matches) > 0 else []
        away_dmrs = away_matches['away_dmr'].values if len(away_matches) > 0 else []
        
        all_dmrs = list(home_dmrs) + list(away_dmrs)
        
        if len(all_dmrs) > 0:
            recent_matches = team_matches.sort_values('date').tail(10)
            recent_dmrs = []
            for _, match in recent_matches.iterrows():
                if match['home_team_api_id'] == team_id:
                    recent_dmrs.append(match['home_dmr'])
                else:
                    recent_dmrs.append(match['away_dmr'])
            
            avg_dmr = np.mean(all_dmrs)
            recent_avg_dmr = np.mean(recent_dmrs) if recent_dmrs else avg_dmr
            
            team_ratings.append({
                'team_api_id': team_id,
                'team_name': team_name,
                'avg_dmr': avg_dmr,
                'recent_dmr': recent_avg_dmr,
                'total_matches': len(team_matches)
            })
    
    df_team_ratings = pd.DataFrame(team_ratings)
    
    # Store in global variables
    _final_clf = final_clf
    _final_reg = final_reg
    _scaler = scaler
    _le = le
    _df_team_ratings = df_team_ratings
    _df_features = df_features
    _df_team = df_team
    _feature_cols = feature_cols
    _models_loaded = True
    
    connection.close()
    conn_draft.close()


def get_team_dmrs(team_names):
    """
    Get DMR ratings for a list of teams.
    
    Args:
        team_names: List of team names (strings) to get DMR for
        
    Returns:
        Dictionary mapping team names to their average DMR values.
        Format: {'Team Name': avg_dmr}
        If a team is not found, it will not be in the result.
    """
    _load_data_and_models()
    
    # Normalize team names for matching
    team_names_normalized = [name.lower().strip() for name in team_names]
    
    # Match teams
    result = {}
    for team_name in team_names:
        team_name_normalized = team_name.lower().strip()
        
        # Find matching team in ratings
        matching_teams = _df_team_ratings[
            _df_team_ratings['team_name'].str.lower().str.strip() == team_name_normalized
        ]
        
        if len(matching_teams) > 0:
            # Use recent_dmr (more current) or avg_dmr as fallback
            dmr = matching_teams.iloc[0]['recent_dmr']
            result[team_name] = float(dmr)
        else:
            # Team not found - could log warning here
            pass
    
    return result


def get_all_team_dmrs():
    """
    Get DMR ratings for all teams in the database.
    
    Returns:
        Dictionary mapping team names to their average DMR values.
        Format: {'Team Name': avg_dmr}
    """
    _load_data_and_models()
    
    result = {}
    for _, row in _df_team_ratings.iterrows():
        result[row['team_name']] = {
            'avg_dmr': float(row['avg_dmr']),
            'recent_dmr': float(row['recent_dmr']),
            'total_matches': int(row['total_matches']),
            'team_api_id': int(row['team_api_id'])
        }
    
    return result

