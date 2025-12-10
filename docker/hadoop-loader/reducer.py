#!/usr/bin/env python3
import sys
import json

# Reducer: Aggregates team stats
# Input: team_id \t role,goals_for,goals_against,win,draw,loss

def reduce_function():
    current_team = None
    stats = {
        'matches': 0,
        'goals_scored': 0.0,
        'goals_conceded': 0.0,
        'wins': 0,
        'draws': 0,
        'losses': 0
    }
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            team_id, data = line.split('\t', 1)
            role, gf, ga, w, d, l = data.split(',')
            
            if current_team != team_id:
                if current_team is not None:
                    # Output result for previous team
                    output_stats(current_team, stats)
                
                # Reset for new team
                current_team = team_id
                stats = {
                    'matches': 0,
                    'goals_scored': 0.0,
                    'goals_conceded': 0.0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0
                }
            
            # Accumulate
            stats['matches'] += 1
            stats['goals_scored'] += float(gf)
            stats['goals_conceded'] += float(ga)
            stats['wins'] += int(w)
            stats['draws'] += int(d)
            stats['losses'] += int(l)
            
        except ValueError:
            continue
    
    # Output last team
    if current_team is not None:
        output_stats(current_team, stats)

def output_stats(team_id, stats):
    # Calculate averages
    matches = stats['matches']
    if matches > 0:
        avg_gf = stats['goals_scored'] / matches
        avg_ga = stats['goals_conceded'] / matches
        win_rate = stats['wins'] / matches
    else:
        avg_gf = 0
        avg_ga = 0
        win_rate = 0
        
    result = {
        'team_id': team_id,
        'total_matches': matches,
        'total_wins': stats['wins'],
        'total_draws': stats['draws'],
        'total_losses': stats['losses'],
        'avg_goals_scored': round(avg_gf, 2),
        'avg_goals_conceded': round(avg_ga, 2),
        'win_rate': round(win_rate, 3)
    }
    
    # Output as tab-separated for Hadoop, but value is JSON
    print(f"{team_id}\t{json.dumps(result)}")

if __name__ == "__main__":
    reduce_function()
