import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import pandas as pd
import numpy as np

# Add the parent directory to sys.path to import machine_learning
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from machine_learning import machine_learning

class TestMachineLearning(unittest.TestCase):

    def setUp(self):
        # Reset global variables in machine_learning before each test
        machine_learning._models_loaded = False
        machine_learning._final_clf = None
        machine_learning._final_reg = None
        machine_learning._scaler = None
        machine_learning._le = None
        machine_learning._df_team_ratings = None
        machine_learning._df_features = None
        machine_learning._df_team = None
        machine_learning._feature_cols = None

    @patch('machine_learning.machine_learning.sqlite3')
    @patch('machine_learning.machine_learning.pd.read_sql_query')
    @patch('machine_learning.machine_learning.os.path.exists')
    @patch('machine_learning.machine_learning.os.path.getsize')
    def test_load_data_and_models_success(self, mock_getsize, mock_exists, mock_read_sql, mock_sqlite3):
        # Mock file existence checks
        mock_exists.return_value = True
        mock_getsize.return_value = 1000  # > 100 bytes

        # Mock database connections
        mock_conn_sqlite = MagicMock()
        mock_sqlite3.connect.return_value = mock_conn_sqlite
        
        # Mock the 'database' module import and get_db_connection
        mock_db_module = MagicMock()
        mock_conn_mysql = MagicMock()
        mock_db_module.get_db_connection.return_value = mock_conn_mysql
        
        with patch.dict(sys.modules, {'database': mock_db_module}):
            # Prepare mock dataframes
            
            # 1. df_match (SQLite)
            # Needs to cover scenarios: Home Win, Away Win, Draw
            df_match_data = {
                'id': [1, 2, 3, 4],
                'home_team_api_id': [101, 102, 101, 103],
                'away_team_api_id': [102, 101, 103, 101],
                'home_team_goal': [2, 1, 1, 0],
                'away_team_goal': [1, 3, 1, 2],
                'date': ['2023-01-01', '2023-01-08', '2023-01-15', '2023-01-22'],
                'league_id': [1, 1, 1, 1]
            }
            df_match = pd.DataFrame(df_match_data)

            # 2. df_team (SQLite)
            # Maps id (external_id) to team_api_id
            df_team_data = {
                'id': [1, 2, 3],
                'team_api_id': [101, 102, 103],
                'team_long_name': ['Team A', 'Team B', 'Team C']
            }
            df_team = pd.DataFrame(df_team_data)

            # 3. df_draft_teams (MySQL - soccer_teams)
            # Needs external_id matching df_team['id']
            df_draft_teams_data = {
                'id': [10, 20, 30],
                'external_id': [1, 2, 3],
                'name': ['Team A', 'Team B', 'Team C']
            }
            df_draft_teams = pd.DataFrame(df_draft_teams_data)

            # Configure read_sql_query side_effect to return correct DF based on query/connection
            # Queries in code:
            # "SELECT * FROM Match" (sqlite)
            # "SELECT * FROM Team" (sqlite)
            # "SELECT * FROM soccer_teams" (mysql)
            
            def read_sql_side_effect(query, conn):
                if "Match" in query:
                    return df_match
                elif "Team" in query:
                    return df_team
                elif "soccer_teams" in query:
                    return df_draft_teams
                return pd.DataFrame()

            mock_read_sql.side_effect = read_sql_side_effect

            # Run the function under test (implicitly via get_team_dmrs)
            # We use get_team_dmrs as it calls _load_data_and_models
            result = machine_learning.get_team_dmrs(['Team A', 'Team B'])

            # Assertions
            
            # Check if models were loaded
            self.assertTrue(machine_learning._models_loaded)
            self.assertIsNotNone(machine_learning._final_clf)
            self.assertIsNotNone(machine_learning._final_reg)
            self.assertIsNotNone(machine_learning._scaler)
            self.assertIsNotNone(machine_learning._le)
            
            # Check results
            # We expect some DMR values. Since we mocked data and models are trained on small data, 
            # exact values are hard to predict without running the math, but they should be floats.
            self.assertIn('Team A', result)
            self.assertIn('Team B', result)
            self.assertIsInstance(result['Team A'], float)
            self.assertIsInstance(result['Team B'], float)
            
            # Check logic flow
            # Should filter matches to only those involving teams 101, 102, 103
            # In our mock data, all matches involve these teams, so all should be used.
            
            # Verify get_all_team_dmrs also works
            all_ratings = machine_learning.get_all_team_dmrs()
            self.assertEqual(len(all_ratings), 3) # Team A, B, C
            self.assertIn('Team C', all_ratings)
            self.assertEqual(all_ratings['Team A']['team_api_id'], 101)

    @patch('machine_learning.machine_learning.sqlite3')
    @patch('machine_learning.machine_learning.pd.read_sql_query')
    @patch('machine_learning.machine_learning.os.path.exists')
    @patch('machine_learning.machine_learning.os.path.getsize')
    def test_load_data_no_matching_teams(self, mock_getsize, mock_exists, mock_read_sql, mock_sqlite3):
        # Scenario where external_id in soccer_teams doesn't match any Team.id
        mock_exists.return_value = True
        mock_getsize.return_value = 1000
        
        mock_db_module = MagicMock()
        mock_db_module.get_db_connection.return_value = MagicMock()
        
        with patch.dict(sys.modules, {'database': mock_db_module}):
            # Mock Data
            df_match = pd.DataFrame({'id': [], 'date': [], 'home_team_api_id': [], 'away_team_api_id': []}) # Empty matches
            df_team = pd.DataFrame({'id': [1], 'team_api_id': [101]})
            df_draft_teams = pd.DataFrame({'external_id': [999]}) # Mismatch
            
            mock_read_sql.side_effect = lambda q, c: df_match if "Match" in q else (df_team if "Team" in q else df_draft_teams)
            
            # Expect ValueError raised by _load_data_and_models
            with self.assertRaises(ValueError) as context:
                machine_learning.get_team_dmrs(['Any Team'])
            
            self.assertIn("No matching teams found", str(context.exception))

if __name__ == '__main__':
    unittest.main()

