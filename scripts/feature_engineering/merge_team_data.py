"""
Script 2: Merge Team Data
Merges game-level stats with lagged season stats.
Drops useless columns (ranks, duplicates, estimated values).

Input:  nba_games_data.csv + nba_stats_lagged.csv
Output: nba_team_game_data.csv (7,880 rows - one per team per game)
"""

import pandas as pd
import numpy as np

def merge_team_data(games_file, stats_file, output_file):
    """
    Merge games and lagged stats, drop useless columns.
    
    Args:
        games_file: Path to games CSV
        stats_file: Path to lagged stats CSV
        output_file: Path for merged output
    """
    print("=" * 80)
    print("STEP 2: MERGING GAMES + LAGGED STATS")
    print("=" * 80)
    
    # Load data
    print("\n1. Loading data...")
    games_df = pd.read_csv(games_file)
    stats_df = pd.read_csv(stats_file)
    print(f"   ✓ Games: {len(games_df):,} rows, {len(games_df.columns)} columns")
    print(f"   ✓ Stats: {len(stats_df):,} rows, {len(stats_df.columns)} columns")
    
    # Define useless columns to drop AFTER merge
    columns_to_drop = [
        # All rank columns (use actual values instead)
        'GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK', 'MIN_RANK',
        'OFF_RATING_RANK', 'DEF_RATING_RANK', 'NET_RATING_RANK',
        'AST_PCT_RANK', 'AST_TO_RANK', 'AST_RATIO_RANK',
        'DREB_PCT_RANK', 'REB_PCT_RANK', 'TS_PCT_RANK',
        'PACE_RANK', 'PIE_RANK',
        'EFG_PCT_RANK_FF', 'FTA_RATE_RANK', 'TM_TOV_PCT_RANK_FF', 'OREB_PCT_RANK_FF',
        'OPP_EFG_PCT_RANK', 'OPP_FTA_RATE_RANK', 'OPP_TOV_PCT_RANK', 'OPP_OREB_PCT_RANK',
        
        # Duplicates (will have _game and _stats suffixes after merge)
        'SEASON_ID',  # Use SEASON instead
        'MIN_game',   # Always 240, not useful
    ]
    
    # Merge on TEAM_ID and GAME_DATE
    print("\n2. Merging on TEAM_ID + GAME_DATE...")
    merged_df = pd.merge(
        games_df,
        stats_df,
        on=['TEAM_ID', 'GAME_DATE'],
        how='inner',
        suffixes=('_game', '_stats')
    )
    print(f"   ✓ Merged: {len(merged_df):,} rows, {len(merged_df.columns)} columns")
    
    if len(merged_df) != len(games_df):
        print(f"   ⚠️  WARNING: Row count changed! Check for merge issues.")
    
    # Drop useless columns that exist
    print("\n3. Dropping useless columns...")
    cols_to_drop_existing = [col for col in columns_to_drop if col in merged_df.columns]
    
    # Also drop duplicate name/season columns, keep _game version
    if 'TEAM_NAME_stats' in merged_df.columns:
        cols_to_drop_existing.append('TEAM_NAME_stats')
    if 'SEASON_stats' in merged_df.columns:
        cols_to_drop_existing.append('SEASON_stats')
    if 'TEAM_ABBR' in merged_df.columns and 'TEAM_ABBREVIATION' in merged_df.columns:
        cols_to_drop_existing.append('TEAM_ABBR')  # Keep TEAM_ABBREVIATION
    
    print(f"   Found {len(cols_to_drop_existing)} columns to drop:")
    for col in sorted(cols_to_drop_existing):
        print(f"     - {col}")
    
    merged_df = merged_df.drop(columns=cols_to_drop_existing)
    print(f"   ✓ Dropped {len(cols_to_drop_existing)} columns")
    
    # Rename duplicate columns for clarity
    print("\n4. Cleaning column names...")
    if 'TEAM_NAME_game' in merged_df.columns:
        merged_df = merged_df.rename(columns={'TEAM_NAME_game': 'TEAM_NAME'})
    if 'SEASON_game' in merged_df.columns:
        merged_df = merged_df.rename(columns={'SEASON_game': 'SEASON'})
    if 'MIN_stats' in merged_df.columns:
        merged_df = merged_df.rename(columns={'MIN_stats': 'MIN_SEASON'})
    
    # Sort by date for consistency
    print("\n5. Sorting by GAME_DATE...")
    merged_df['GAME_DATE'] = pd.to_datetime(merged_df['GAME_DATE'])
    merged_df = merged_df.sort_values(['TEAM_ID', 'GAME_DATE']).reset_index(drop=True)
    
    # Verify data quality
    print("\n6. Data quality checks...")
    print(f"   Unique games: {merged_df['GAME_ID'].nunique():,}")
    print(f"   Unique teams: {merged_df['TEAM_ID'].nunique()}")
    print(f"   Date range: {merged_df['GAME_DATE'].min().date()} to {merged_df['GAME_DATE'].max().date()}")
    
    # Check for NaN in PRIOR columns (should be ~30)
    prior_cols = [col for col in merged_df.columns if col.endswith('_PRIOR')]
    if prior_cols:
        null_count = merged_df[prior_cols[0]].isnull().sum()
        print(f"   Rows with NaN in PRIOR columns: {null_count} (first game per team)")
    
    # Save output
    print(f"\n7. Saving merged data...")
    merged_df.to_csv(output_file, index=False)
    print(f"   ✓ Saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("-" * 80)
    print(f"Total rows:    {len(merged_df):,}")
    print(f"Total columns: {len(merged_df.columns)}")
    print(f"Format:        One row per TEAM per GAME")
    print(f"Structure:     Still 2 rows per actual game (one for each team)")
    print("=" * 80)
    
    return merged_df


if __name__ == "__main__":
    # File paths
    GAMES_FILE = "data/raw/nba/nba_games_data.csv"
    STATS_FILE = "data/processed/nba/nba_stats_lagged.csv"
    OUTPUT_FILE = "data/processed/nba/nba_team_game_data.csv"
    
    # Run the merge
    df_merged = merge_team_data(GAMES_FILE, STATS_FILE, OUTPUT_FILE)
    
    print("\n✅ STEP 2 COMPLETE: Team-level data merged successfully!")
    print(f"Next: Run script 03_create_game_level.py to consolidate into one row per game")