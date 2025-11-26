"""
NBA Data Collection Helper Functions
Created: 2025-11-24

This module contains reusable helper functions for NBA data collection.
Import these functions in your scripts for consistent data handling.

USAGE:
    from scripts.data_collection.helpers import get_all_team_ids, get_team_id
"""

from nba_api.stats.static import teams
import pandas as pd
import time

# ============================================================
# TEAM HELPERS
# ============================================================

def get_all_team_ids():
    """
    Get dictionary of all NBA teams with their IDs
    
    Returns:
        dict: {team_abbr: team_id}
    
    Example:
        >>> team_ids = get_all_team_ids()
        >>> print(team_ids['LAL'])
        1610612747
    """
    all_teams = teams.get_teams()
    return {team['abbreviation']: team['id'] for team in all_teams}

def get_team_id(team_abbr):
    """
    Get NBA team ID from team abbreviation
    
    Args:
        team_abbr (str): Team abbreviation (e.g., 'LAL', 'GSW')
    
    Returns:
        int: Team ID or None if not found
    
    Example:
        >>> lakers_id = get_team_id('LAL')
        >>> print(lakers_id)
        1610612747
    """
    all_teams = teams.get_teams()
    team = [t for t in all_teams if t['abbreviation'] == team_abbr]
    return team[0]['id'] if team else None

def get_team_info(team_abbr):
    """
    Get full team information from abbreviation
    
    Args:
        team_abbr (str): Team abbreviation (e.g., 'LAL')
    
    Returns:
        dict: Full team information or None if not found
    
    Example:
        >>> lakers_info = get_team_info('LAL')
        >>> print(lakers_info['full_name'])
        'Los Angeles Lakers'
    """
    all_teams = teams.get_teams()
    team = [t for t in all_teams if t['abbreviation'] == team_abbr]
    return team[0] if team else None

def get_all_teams():
    """
    Get list of all NBA teams with full information
    
    Returns:
        list: List of team dictionaries
    
    Example:
        >>> all_teams = get_all_teams()
        >>> print(len(all_teams))
        30
    """
    return teams.get_teams()

# ============================================================
# DATA HELPERS
# ============================================================

def rate_limit(delay=0.6):
    """
    Simple rate limiting function
    
    Args:
        delay (float): Seconds to wait (default: 0.6)
    
    Example:
        >>> rate_limit()  # Wait 0.6 seconds
        >>> rate_limit(1.0)  # Wait 1 second
    """
    time.sleep(delay)

def save_checkpoint(df, filepath):
    """
    Save DataFrame as checkpoint during collection
    
    Args:
        df (pd.DataFrame): Data to save
        filepath (str): Path to save checkpoint
    
    Example:
        >>> save_checkpoint(games_df, 'checkpoint_games.csv')
    """
    df.to_csv(filepath, index=False)
    print(f"✅ Checkpoint saved: {filepath} ({len(df):,} records)")

def load_checkpoint(filepath):
    """
    Load checkpoint file if it exists
    
    Args:
        filepath (str): Path to checkpoint file
    
    Returns:
        pd.DataFrame or None: Loaded data or None if file doesn't exist
    
    Example:
        >>> existing_data = load_checkpoint('checkpoint_games.csv')
        >>> if existing_data is not None:
        >>>     print(f"Loaded {len(existing_data)} existing records")
    """
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Checkpoint loaded: {filepath} ({len(df):,} records)")
        return df
    except FileNotFoundError:
        print(f"⚠️  No checkpoint found: {filepath}")
        return None

# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_season_format(season):
    """
    Validate season string format
    
    Args:
        season (str): Season string (e.g., '2023-24')
    
    Returns:
        bool: True if valid format
    
    Example:
        >>> validate_season_format('2023-24')
        True
        >>> validate_season_format('2023')
        False
    """
    import re
    pattern = r'^\d{4}-\d{2}$'
    return bool(re.match(pattern, season))

def validate_team_abbr(team_abbr):
    """
    Validate if team abbreviation exists
    
    Args:
        team_abbr (str): Team abbreviation to validate
    
    Returns:
        bool: True if valid team abbreviation
    
    Example:
        >>> validate_team_abbr('LAL')
        True
        >>> validate_team_abbr('XXX')
        False
    """
    all_team_ids = get_all_team_ids()
    return team_abbr in all_team_ids

def count_expected_games(num_seasons=4, games_per_season=1230):
    """
    Calculate expected number of game records
    
    Args:
        num_seasons (int): Number of seasons
        games_per_season (int): Games per season (default: 1230)
    
    Returns:
        int: Expected number of records (2 per game for both teams)
    
    Example:
        >>> expected = count_expected_games(4)
        >>> print(f"Expected records: {expected:,}")
        Expected records: 9,840
    """
    return num_seasons * games_per_season * 2  # 2 records per game

# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_collection_summary(df, dataset_name='Dataset'):
    """
    Print summary statistics for collected data
    
    Args:
        df (pd.DataFrame): Collected data
        dataset_name (str): Name of dataset for display
    
    Example:
        >>> print_collection_summary(games_df, 'NBA Games')
    """
    print("\n" + "="*60)
    print(f"{dataset_name.upper()} COLLECTION SUMMARY")
    print("="*60)
    print(f"📊 Total Records: {len(df):,}")
    print(f"📅 Columns: {len(df.columns)}")
    
    if 'SEASON' in df.columns:
        print(f"🏀 Seasons: {sorted(df['SEASON'].unique())}")
    
    if 'GAME_ID' in df.columns:
        print(f"🎮 Unique Games: {df['GAME_ID'].nunique():,}")
    
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        print(f"\n⚠️  Missing Values:")
        print(missing)
    else:
        print(f"\n✅ No missing values")
    
    print("="*60 + "\n")

# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("NBA Data Collection Helpers - Usage Examples")
    print("="*60)
    
    # Example 1: Get all team IDs
    print("\n1. Get all team IDs:")
    team_ids = get_all_team_ids()
    print(f"   Total teams: {len(team_ids)}")
    print(f"   Sample: LAL={team_ids['LAL']}, GSW={team_ids['GSW']}")
    
    # Example 2: Get specific team info
    print("\n2. Get Lakers information:")
    lakers_info = get_team_info('LAL')
    print(f"   Full name: {lakers_info['full_name']}")
    print(f"   City: {lakers_info['city']}")
    
    # Example 3: Validate inputs
    print("\n3. Validation examples:")
    print(f"   '2023-24' is valid season: {validate_season_format('2023-24')}")
    print(f"   'LAL' is valid team: {validate_team_abbr('LAL')}")
    print(f"   'XXX' is valid team: {validate_team_abbr('XXX')}")
    
    # Example 4: Expected records
    print("\n4. Expected data size:")
    expected = count_expected_games(4)
    print(f"   4 seasons × 1,230 games × 2 records = {expected:,} total records")
    
    print("\n" + "="*60)
    print("✅ All examples complete")
    
    
# ============================================================
# DATASET SPLITTING
# ============================================================
    
    
import pandas as pd

class TemporalSplitter:
    def __init__(self, date_col="GAME_DATE"):
        self.date_col = date_col

    def split(self, df, train=0.70, val=0.15, test=0.15):
        df = df.sort_values(self.date_col).reset_index(drop=True)
        n = len(df)

        train_end = int(n * train)
        val_end = int(n * (train + val))

        train_df = df.iloc[:train_end]
        val_df = df.iloc[train_end:val_end]
        test_df = df.iloc[val_end:]

        return train_df, val_df, test_df

    def summary(self, df, train_df, val_df, test_df):
        n = len(df)
        return {
            "train_rows": len(train_df),
            "val_rows": len(val_df),
            "test_rows": len(test_df),
            "train_pct": len(train_df)/n,
            "val_pct": len(val_df)/n,
            "test_pct": len(test_df)/n
        }
