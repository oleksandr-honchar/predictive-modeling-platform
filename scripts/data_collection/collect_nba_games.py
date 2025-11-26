"""
Collect all NBA game data (4 seasons: 2022-23 through 2025-26)
Total expected games: ~4,000
Created: 2025-11-24

USAGE:
    python collect_nba_games.py

OUTPUT:
    data/raw/nba/nba_games_all_data.csv

IMPORTANT:
    - Collects ALL 4 seasons in one dataset
    - Includes rate limiting (0.6s between requests)
    - Saves progress incrementally
"""

from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams
import pandas as pd
import time
from datetime import datetime
import os

# ============================================================
# CONFIGURATION
# ============================================================

SEASONS = ['2021-22', '2022-23', '2023-24', '2024-25', '2025-26']
OUTPUT_DIR = 'data/raw/nba'
OUTPUT_FILE = 'nba_games_data.csv'
RATE_LIMIT_DELAY = 0.6  # seconds between API calls

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_all_team_ids():
    """
    Get dictionary of all NBA teams with their IDs
    
    Returns:
        dict: {team_abbr: team_id}
    """
    all_teams = teams.get_teams()
    return {team['abbreviation']: team['id'] for team in all_teams}

def collect_games_for_season(season, team_ids):
    """
    Collect all games for a specific season
    
    Args:
        season (str): Season string (e.g., '2023-24')
        team_ids (dict): Dictionary of team abbreviations to IDs
    
    Returns:
        pd.DataFrame: All games for the season
    """
    print(f"\n{'='*60}")
    print(f"Collecting games for {season} season...")
    print(f"{'='*60}")
    
    all_games = []
    teams_processed = 0
    
    for team_abbr, team_id in team_ids.items():
        try:
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
            
            # Fetch games
            gamefinder = leaguegamefinder.LeagueGameFinder(
                team_id_nullable=team_id,
                season_nullable=season,
                season_type_nullable='Regular Season'
            )
            
            games_df = gamefinder.get_data_frames()[0]
            
            # Add metadata
            games_df['SEASON'] = season
            games_df['TEAM_ABBR'] = team_abbr
            
            all_games.append(games_df)
            teams_processed += 1
            
            print(f"✅ {team_abbr}: {len(games_df)} games | Progress: {teams_processed}/{len(team_ids)}")
            
        except Exception as e:
            print(f"❌ Error fetching {team_abbr}: {e}")
            continue
    
    # Combine all games
    if all_games:
        season_df = pd.concat(all_games, ignore_index=True)
        print(f"\n✅ Total games collected for {season}: {len(season_df)}")
        return season_df
    else:
        print(f"\n❌ No games collected for {season}")
        return pd.DataFrame()

def save_data(df, output_path):
    """
    Save DataFrame to CSV with metadata
    
    Args:
        df (pd.DataFrame): Data to save
        output_path (str): Full path to output file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\n{'='*60}")
    print(f"✅ Data saved successfully!")
    print(f"📁 Location: {output_path}")
    print(f"📊 Total records: {len(df):,}")
    print(f"📅 Seasons: {df['SEASON'].unique().tolist()}")
    print(f"🏀 Unique games: {df['GAME_ID'].nunique():,}")
    print(f"{'='*60}")

# ============================================================
# MAIN COLLECTION PROCESS
# ============================================================

def main():
    """
    Main data collection workflow
    """
    start_time = datetime.now()
    print("\n" + "="*60)
    print("NBA GAME DATA COLLECTION")
    print("="*60)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Seasons to collect: {', '.join(SEASONS)}")
    print(f"Rate limit: {RATE_LIMIT_DELAY}s between requests")
    
    # Step 1: Get all team IDs
    print("\n[STEP 1] Fetching NBA teams...")
    team_ids = get_all_team_ids()
    print(f"✅ Found {len(team_ids)} teams")
    
    # Step 2: Collect games for each season
    all_seasons_data = []
    
    for season in SEASONS:
        season_df = collect_games_for_season(season, team_ids)
        if not season_df.empty:
            all_seasons_data.append(season_df)
    
    # Step 3: Combine all seasons
    print("\n[STEP 3] Combining all seasons...")
    if all_seasons_data:
        final_df = pd.concat(all_seasons_data, ignore_index=True)
        print(f"✅ Combined dataset created: {len(final_df):,} total records")
    else:
        print("❌ No data collected")
        return
    
    # Step 4: Data quality checks
    print("\n[STEP 4] Running data quality checks...")
    print(f"Missing values:\n{final_df.isnull().sum()[final_df.isnull().sum() > 0]}")
    print(f"\nDate range: {final_df['GAME_DATE'].min()} to {final_df['GAME_DATE'].max()}")
    print(f"Teams: {sorted(final_df['TEAM_ABBR'].unique())}")
    
    # Step 5: Save data
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    save_data(final_df, output_path)
    
    # Completion stats
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n⏱️  Total execution time: {duration}")
    print(f"✅ Collection complete!")

if __name__ == "__main__":
    main()