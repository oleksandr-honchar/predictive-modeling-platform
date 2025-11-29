"""
Improved NBA Game Data Collection
==================================
Collects games in MATCHUP format (1 row per game, not 2)
Much more efficient and easier to process

Seasons: 2020-21 through 2025-26
Expected games: ~6,100 games (includes Game 1 of each season)

USAGE:
    python collect_nba_games_improved.py

OUTPUT:
    data/raw/nba/nba_games_all_seasons_RAW.csv
    
KEY DIFFERENCE:
    - Gets ALL games at once (not per team)
    - No duplicates
    - Already in matchup format
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

SEASONS = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25', '2025-26']
OUTPUT_DIR = 'data/raw/nba'
OUTPUT_FILE = 'nba_games_all_seasons_RAW.csv'
RATE_LIMIT_DELAY = 2.0  # Be conservative with API

# ============================================================
# MAIN COLLECTION
# ============================================================

def collect_all_games_for_season(season):
    """
    Collect ALL games for a season at once.
    Returns data in team-game format (2 rows per game).
    
    Args:
        season (str): Season like '2024-25'
    
    Returns:
        pd.DataFrame: All team-game records
    """
    print(f"\nCollecting {season}...")
    
    try:
        # Get ALL games for the season (not per team!)
        gamefinder = leaguegamefinder.LeagueGameFinder(
            season_nullable=season,
            season_type_nullable='Regular Season',
            league_id_nullable='00'  # NBA
        )
        
        games_df = gamefinder.get_data_frames()[0]
        games_df['SEASON'] = season
        
        # Get unique game count
        unique_games = games_df['GAME_ID'].nunique()
        
        print(f"✓ {season}: {len(games_df)} team-game records ({unique_games} unique games)")
        
        return games_df
        
    except Exception as e:
        print(f"✗ Error collecting {season}: {e}")
        return pd.DataFrame()


def convert_to_matchup_format(games_df):
    """
    Convert from team-game format (2 rows per game) 
    to matchup format (1 row per game with HOME/AWAY columns).
    
    This is the format you need for feature engineering!
    """
    print("\nConverting to matchup format...")
    
    # Identify home vs away games
    games_df['IS_HOME'] = games_df['MATCHUP'].str.contains('vs.')
    
    # Split into home and away
    home_games = games_df[games_df['IS_HOME'] == True].copy()
    away_games = games_df[games_df['IS_HOME'] == False].copy()
    
    print(f"  Home game records: {len(home_games)}")
    print(f"  Away game records: {len(away_games)}")
    
    # Add prefixes
    home_games = home_games.add_prefix('HOME_')
    away_games = away_games.add_prefix('AWAY_')
    
    # Merge on GAME_ID
    matchups = home_games.merge(
        away_games,
        left_on='HOME_GAME_ID',
        right_on='AWAY_GAME_ID',
        how='inner'
    )
    
    # Clean up
    matchups = matchups.rename(columns={'HOME_GAME_ID': 'GAME_ID'})
    
    # Add useful columns
    matchups['GAME_DATE'] = pd.to_datetime(matchups['HOME_GAME_DATE'])
    matchups['SEASON'] = matchups['HOME_SEASON']
    matchups['HOME_WIN'] = (matchups['HOME_WL'] == 'W').astype(int)
    
    # Select key columns to keep (add more if needed)
    keep_cols = [
        'GAME_ID', 'GAME_DATE', 'SEASON',
        'HOME_TEAM_ID', 'HOME_TEAM_ABBREVIATION', 'HOME_TEAM_NAME',
        'AWAY_TEAM_ID', 'AWAY_TEAM_ABBREVIATION', 'AWAY_TEAM_NAME',
        'HOME_WIN', 'HOME_WL', 'AWAY_WL',
        'HOME_PTS', 'AWAY_PTS',
        'HOME_FGM', 'HOME_FGA', 'HOME_FG_PCT',
        'AWAY_FGM', 'AWAY_FGA', 'AWAY_FG_PCT',
        'HOME_FG3M', 'HOME_FG3A', 'HOME_FG3_PCT',
        'AWAY_FG3M', 'AWAY_FG3A', 'AWAY_FG3_PCT',
        'HOME_FTM', 'HOME_FTA', 'HOME_FT_PCT',
        'AWAY_FTM', 'AWAY_FTA', 'AWAY_FT_PCT',
        'HOME_OREB', 'HOME_DREB', 'HOME_REB',
        'AWAY_OREB', 'AWAY_DREB', 'AWAY_REB',
        'HOME_AST', 'HOME_STL', 'HOME_BLK', 'HOME_TOV', 'HOME_PF',
        'AWAY_AST', 'AWAY_STL', 'AWAY_BLK', 'AWAY_TOV', 'AWAY_PF',
        'HOME_PLUS_MINUS', 'AWAY_PLUS_MINUS'
    ]
    
    # Keep only columns that exist
    keep_cols = [col for col in keep_cols if col in matchups.columns]
    matchups = matchups[keep_cols]
    
    print(f"✓ Converted to {len(matchups)} matchup records")
    print(f"  Columns: {len(matchups.columns)}")
    
    return matchups


def save_with_metadata(df, output_path):
    """Save data with summary statistics."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    
    print("\n" + "="*70)
    print("✓ DATA SAVED SUCCESSFULLY")
    print("="*70)
    print(f"Location: {output_path}")
    print(f"Total games: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Date range: {df['GAME_DATE'].min().date()} to {df['GAME_DATE'].max().date()}")
    print(f"Seasons: {sorted(df['SEASON'].unique())}")
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"\n⚠️  Columns with missing values:")
        print(missing[missing > 0])
    else:
        print(f"\n✓ No missing values!")
    
    print("="*70)


def main():
    """Main collection workflow."""
    start_time = datetime.now()
    
    print("\n" + "="*70)
    print("NBA GAME DATA COLLECTION (IMPROVED)")
    print("="*70)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Seasons: {', '.join(SEASONS)}")
    print(f"Output: {os.path.join(OUTPUT_DIR, OUTPUT_FILE)}")
    
    # Collect all seasons
    all_seasons = []
    
    for season in SEASONS:
        games = collect_all_games_for_season(season)
        
        if not games.empty:
            all_seasons.append(games)
        
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
    
    if not all_seasons:
        print("\n✗ No data collected!")
        return
    
    # Combine all seasons
    print("\nCombining all seasons...")
    all_games = pd.concat(all_seasons, ignore_index=True)
    print(f"✓ Total records: {len(all_games):,}")
    
    # Convert to matchup format
    matchups = convert_to_matchup_format(all_games)
    
    # Sort by date
    matchups = matchups.sort_values('GAME_DATE').reset_index(drop=True)
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    save_with_metadata(matchups, output_path)
    
    # Stats
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n⏱️  Execution time: {duration}")
    print(f"✓ Collection complete!")
    
    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. ✓ You now have raw game data in matchup format")
    print("2. → Next: Collect team advanced statistics")
    print("3. → Then: Merge stats to create _PRIOR columns")
    print("4. → Then: Run feature engineering")
    print("5. → Finally: Filter early games and train model")
    print("="*70)


if __name__ == "__main__":
    main()