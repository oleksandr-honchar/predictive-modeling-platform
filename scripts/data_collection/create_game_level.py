"""
Script 3: Create Game-Level Dataset
Transforms data from 7,880 rows (one per team per game) to 3,940 rows (one per game).
Adds HOME_ and AWAY_ prefixes to distinguish teams.

Input:  nba_team_game_data.csv (7,880 rows)
Output: nba_game_level_data.csv (3,940 rows)
"""

import pandas as pd
import numpy as np

def create_game_level_data(input_file, output_file):
    """
    Convert team-level data to game-level data.
    Each game gets one row with HOME and AWAY team columns.
    
    Args:
        input_file: Path to team-game CSV (7,880 rows)
        output_file: Path for game-level CSV (3,940 rows)
    """
    print("=" * 80)
    print("STEP 3: CREATING GAME-LEVEL DATASET")
    print("=" * 80)
    
    # Load data
    print("\n1. Loading team-level data...")
    df = pd.read_csv(input_file)
    print(f"   ✓ Loaded {len(df):,} rows (2 per game)")
    
    # Parse MATCHUP to identify home/away
    print("\n2. Identifying home vs away teams...")
    df['IS_HOME'] = df['MATCHUP'].str.contains('vs.').astype(int)
    print(f"   ✓ Home games: {df['IS_HOME'].sum():,}")
    print(f"   ✓ Away games: {(1 - df['IS_HOME']).sum():,}")
    
    # Separate home and away
    print("\n3. Separating home and away team data...")
    home_df = df[df['IS_HOME'] == 1].copy()
    away_df = df[df['IS_HOME'] == 0].copy()
    
    print(f"   ✓ Home team rows: {len(home_df):,}")
    print(f"   ✓ Away team rows: {len(away_df):,}")
    
    # Verify same number of home and away games
    if len(home_df) != len(away_df):
        print(f"   ⚠️  WARNING: Unequal home/away counts!")
    
    # Columns to exclude from prefixing (keep once per game)
    game_level_cols = ['GAME_ID', 'GAME_DATE', 'SEASON']
    
    # Columns to prefix with HOME_ or AWAY_
    cols_to_prefix = [col for col in home_df.columns 
                     if col not in game_level_cols + ['IS_HOME', 'MATCHUP']]
    
    print(f"\n4. Renaming columns with HOME_ and AWAY_ prefixes...")
    print(f"   Columns to prefix: {len(cols_to_prefix)}")
    
    # Rename home columns
    home_rename = {col: f'HOME_{col}' for col in cols_to_prefix}
    home_df = home_df.rename(columns=home_rename)
    
    # Rename away columns  
    away_rename = {col: f'AWAY_{col}' for col in cols_to_prefix}
    away_df = away_df.rename(columns=away_rename)
    
    # Keep only renamed columns + game identifiers
    home_cols = game_level_cols + [f'HOME_{col}' for col in cols_to_prefix]
    away_cols = game_level_cols + [f'AWAY_{col}' for col in cols_to_prefix]
    
    home_df = home_df[home_cols]
    away_df = away_df[away_cols]
    
    # Merge home and away into single game-level row
    print("\n5. Merging home and away data...")
    game_df = pd.merge(
        home_df,
        away_df,
        on=game_level_cols,
        how='inner',
        validate='1:1'  # Ensure exactly one home matches one away
    )
    
    print(f"   ✓ Game-level rows: {len(game_df):,}")
    print(f"   ✓ Total columns: {len(game_df.columns)}")
    
    # Verify no data loss
    if len(game_df) != len(home_df):
        print(f"   ⚠️  WARNING: Lost {len(home_df) - len(game_df)} games in merge!")
    
    # Create target variable (HOME_WIN)
    print("\n6. Creating target variable...")
    game_df['HOME_WIN'] = (game_df['HOME_WL'] == 'W').astype(int)
    print(f"   ✓ Created HOME_WIN target")
    print(f"   Home wins: {game_df['HOME_WIN'].sum():,} ({game_df['HOME_WIN'].mean()*100:.1f}%)")
    print(f"   Away wins: {(1-game_df['HOME_WIN']).sum():,} ({(1-game_df['HOME_WIN']).mean()*100:.1f}%)")
    
    # Sort by date
    print("\n7. Sorting by game date...")
    game_df['GAME_DATE'] = pd.to_datetime(game_df['GAME_DATE'])
    game_df = game_df.sort_values('GAME_DATE').reset_index(drop=True)
    
    # Data quality checks
    print("\n8. Data quality checks...")
    print(f"   Unique games: {game_df['GAME_ID'].nunique():,}")
    print(f"   Date range: {game_df['GAME_DATE'].min().date()} to {game_df['GAME_DATE'].max().date()}")
    print(f"   Seasons: {sorted(game_df['SEASON'].unique())}")
    
    # Check for NaN
    null_counts = game_df.isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if len(cols_with_nulls) > 0:
        print(f"\n   Columns with NaN values: {len(cols_with_nulls)}")
        print("   (These are from first games - will handle in next script)")
    else:
        print("\n   ✓ No NaN values found")
    
    # Save output
    print(f"\n9. Saving game-level data...")
    game_df.to_csv(output_file, index=False)
    print(f"   ✓ Saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("-" * 80)
    print(f"Input rows:    {len(df):,} (team-level)")
    print(f"Output rows:   {len(game_df):,} (game-level)")
    print(f"Columns:       {len(game_df.columns)}")
    print(f"Format:        One row per GAME")
    print(f"Structure:     HOME_* and AWAY_* columns for each stat")
    print(f"Target:        HOME_WIN (1 = home win, 0 = away win)")
    print("=" * 80)
    
    return game_df


if __name__ == "__main__":
    # File paths
    INPUT_FILE = "data/processed/nba/nba_team_game_data.csv"
    OUTPUT_FILE = "data/processed/nba/nba_game_level_data.csv"
    
    # Run the transformation
    df_game = create_game_level_data(INPUT_FILE, OUTPUT_FILE)
    
    print("\n✅ STEP 3 COMPLETE: Game-level dataset created!")
    print(f"Next: Run script 04_add_features.py to add derived features")