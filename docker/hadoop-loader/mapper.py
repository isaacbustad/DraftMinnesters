#!/usr/bin/env python3
import sys
import csv

# Mapper: processing match data to emit team stats
# Input format (CSV): id, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal

def map_function():
    # Use csv reader to handle potential edge cases
    reader = csv.reader(sys.stdin)
    
    for row in reader:
        if len(row) < 6:
            continue
            
        try:
            # Skip header if present
            if row[0] == 'id':
                continue
                
            match_id = row[0]
            date = row[1]
            home_team_id = row[2]
            away_team_id = row[3]
            home_goals = float(row[4])
            away_goals = float(row[5])
            
            # Emit for Home Team
            # format: team_id \t role,goals_for,goals_against,win,draw,loss
            home_win = 1 if home_goals > away_goals else 0
            home_draw = 1 if home_goals == away_goals else 0
            home_loss = 1 if home_goals < away_goals else 0
            
            print(f"{home_team_id}\tHOME,{home_goals},{away_goals},{home_win},{home_draw},{home_loss}")
            
            # Emit for Away Team
            away_win = 1 if away_goals > home_goals else 0
            away_draw = 1 if away_goals == home_goals else 0
            away_loss = 1 if away_goals < home_goals else 0
            
            print(f"{away_team_id}\tAWAY,{away_goals},{home_goals},{away_win},{away_draw},{away_loss}")
            
        except ValueError:
            continue

if __name__ == "__main__":
    map_function()
