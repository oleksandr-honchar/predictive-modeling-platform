"""
Test nba_api endpoints and create helper functions
Created: 2025-11-24
Purpose: Verify nba_api installation and test key endpoints
"""

from nba_api.stats.endpoints import leaguegamefinder, teamdashboardbygeneralsplits
from nba_api.stats.static import teams
import pandas as pd
import time

print("=" * 60)
print("NBA API TESTING SUITE")
print("=" * 60)

# Test 1: Get all NBA teams
print("\n[TEST 1] Fetching all NBA teams...")
all_teams = teams.get_teams()
print(f"✅ Successfully retrieved {len(all_teams)} NBA teams")
print(f"Sample team: {all_teams[0]}")

# Test 2: Test LeagueGameFinder for a small sample
print("\n[TEST 2] Testing LeagueGameFinder endpoint...")
print("Fetching Lakers games from 2023-24 season...")

try:
    # Find Lakers team_id
    lakers = [team for team in all_teams if team['abbreviation'] == 'LAL'][0]
    lakers_id = lakers['id']
    print(f"Lakers Team ID: {lakers_id}")
    
    # Fetch games
    time.sleep(1)  # Rate limiting
    gamefinder = leaguegamefinder.LeagueGameFinder(
        team_id_nullable=lakers_id,
        season_nullable='2023-24',
        season_type_nullable='Regular Season'
    )
    
    games_df = gamefinder.get_data_frames()[0]
    print(f"✅ Successfully retrieved {len(games_df)} Lakers games")
    print(f"\nSample columns: {list(games_df.columns[:10])}")
    print(f"\nFirst game:\n{games_df.head(1).T}")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Test TeamDashboard for advanced stats
print("\n[TEST 3] Testing TeamDashboardByGeneralSplits endpoint...")
print("Fetching Lakers advanced stats from 2023-24 season...")

try:
    time.sleep(1)  # Rate limiting
    team_dashboard = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(
        team_id=lakers_id,
        season='2023-24',
        season_type_all_star='Regular Season'
    )
    
    overall_stats = team_dashboard.get_data_frames()[0]
    print(f"✅ Successfully retrieved advanced stats")
    print(f"\nAvailable columns: {list(overall_stats.columns)}")
    print(f"\nStats preview:\n{overall_stats.head()}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("HELPER FUNCTIONS")
print("=" * 60)

# Helper Function 1: Get team ID by abbreviation
def get_team_id(team_abbr):
    """
    Get NBA team ID from team abbreviation
    
    Args:
        team_abbr (str): Team abbreviation (e.g., 'LAL', 'GSW')
    
    Returns:
        int: Team ID or None if not found
    """
    all_teams = teams.get_teams()
    team = [t for t in all_teams if t['abbreviation'] == team_abbr]
    return team[0]['id'] if team else None

# Helper Function 2: Get all team IDs
def get_all_team_ids():
    """
    Get dictionary of all NBA teams with their IDs
    
    Returns:
        dict: {team_abbr: team_id}
    """
    all_teams = teams.get_teams()
    return {team['abbreviation']: team['id'] for team in all_teams}

# Test helper functions
print("\n[HELPER TEST] Testing helper functions...")
test_id = get_team_id('LAL')
print(f"get_team_id('LAL'): {test_id}")

all_team_ids = get_all_team_ids()
print(f"\nget_all_team_ids() - Total teams: {len(all_team_ids)}")
print(f"Sample: {list(all_team_ids.items())[:5]}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED")
print("=" * 60)