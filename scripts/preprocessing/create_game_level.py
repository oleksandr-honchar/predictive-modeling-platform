"""
Script: Create Game-Level Dataset (CORRECT VERSION - HANDLES NEUTRAL VENUES)
=============================================================================
This version CORRECTLY handles neutral venue games where both teams show @.

Strategy:
1. Detect neutral venue games (both teams have @)
2. For neutral games: Designate first team alphabetically as "home"
3. For regular games: Use vs./@ as normal

This ensures NO GAMES ARE LOST while keeping code simple.

Author: Oleksandr
Date: November 25, 2024
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def create_game_level_data(input_file, output_file):
    """
    Convert team-level data to game-level data.
    CORRECTLY handles neutral venue games.
    
    Args:
        input_file: Path to team-game CSV (team-level, 2 rows per game)
        output_file: Path for game-level CSV (1 row per game)
    
    Returns:
        pd.DataFrame: Game-level data
    """
    print("=" * 80)
    print("STEP 3: CREATING GAME-LEVEL DATASET")
    print("=" * 80)
    
    # ========================================================================
    # 1. LOAD DATA
    # ========================================================================
    print("\n1. Loading team-level data...")
    df = pd.read_csv(input_file)
    print(f"   ✓ Loaded {len(df):,} rows (2 per game)")
    print(f"   ✓ Unique games: {df['GAME_ID'].nunique():,}")
    print(f"   ✓ Date range: {df['GAME_DATE'].min()} to {df['GAME_DATE'].max()}")
    
    if 'SEASON' in df.columns:
        seasons = sorted(df['SEASON'].unique())
        print(f"   ✓ Seasons: {', '.join(seasons)}")
    
    # ========================================================================
    # 2. DETECT NEUTRAL VENUE GAMES (SIMPLE METHOD)
    # ========================================================================
    print("\n2. Detecting neutral venue games...")
    
    # For each game, count how many teams have @ in MATCHUP
    df['has_at'] = df['MATCHUP'].str.contains('@', na=False).astype(int)
    away_counts = df.groupby('GAME_ID')['has_at'].sum()
    
    # Neutral venue: both teams show @ (count = 2)
    neutral_game_ids = away_counts[away_counts == 2].index.tolist()
    df['is_neutral'] = df['GAME_ID'].isin(neutral_game_ids).astype(int)
    
    n_neutral = len(neutral_game_ids)
    n_total = df['GAME_ID'].nunique()
    
    print(f"   ✓ Neutral venue games: {n_neutral}")
    print(f"   ✓ Regular games: {n_total - n_neutral}")
    print(f"   ✓ Neutral %: {n_neutral / n_total * 100:.2f}%")
    
    # ========================================================================
    # 3. ASSIGN HOME/AWAY DESIGNATION
    # ========================================================================
    print("\n3. Assigning home/away designations...")
    
    # Initialize
    df['IS_HOME'] = 0
    
    # REGULAR GAMES: Use vs./@ logic
    regular_games = df['is_neutral'] == 0
    df.loc[regular_games & df['MATCHUP'].str.contains('vs.', na=False), 'IS_HOME'] = 1
    
    # NEUTRAL VENUE GAMES: Assign first team alphabetically as "home"
    if n_neutral > 0:
        print(f"\n   Handling {n_neutral} neutral venue games...")
        
        for game_id in neutral_game_ids:
            game_rows = df[df['GAME_ID'] == game_id]
            teams = game_rows['TEAM_ABBREVIATION'].tolist()
            
            # First team alphabetically = "home" (arbitrary but consistent)
            home_team = sorted(teams)[0]
            
            df.loc[(df['GAME_ID'] == game_id) & 
                   (df['TEAM_ABBREVIATION'] == home_team), 'IS_HOME'] = 1
        
        print(f"   ✓ Assigned home designation (alphabetically) for neutral games")
    
    # Verify counts
    home_count = (df['IS_HOME'] == 1).sum()
    away_count = (df['IS_HOME'] == 0).sum()
    
    print(f"\n   Final designations:")
    print(f"   ✓ Home teams: {home_count:,}")
    print(f"   ✓ Away teams: {away_count:,}")
    
    if home_count == away_count:
        print(f"   ✅ Perfect: Equal home/away counts")
    else:
        print(f"   ⚠️  Imbalanced: {abs(home_count - away_count)} difference")
    
    # ========================================================================
    # 4. SEPARATE HOME AND AWAY
    # ========================================================================
    print("\n4. Separating home and away team data...")
    
    home_df = df[df['IS_HOME'] == 1].copy()
    away_df = df[df['IS_HOME'] == 0].copy()
    
    print(f"   ✓ Home team rows: {len(home_df):,}")
    print(f"   ✓ Away team rows: {len(away_df):,}")
    
    # ========================================================================
    # 5. RENAME COLUMNS WITH PREFIXES
    # ========================================================================
    print("\n5. Renaming columns with HOME_ and AWAY_ prefixes...")
    
    # Columns to keep at game level (no prefix)
    game_level_cols = ['GAME_ID', 'GAME_DATE', 'SEASON']
    
    # Columns to prefix
    cols_to_prefix = [col for col in home_df.columns 
                     if col not in game_level_cols + ['IS_HOME', 'MATCHUP', 'has_at', 'is_neutral']]
    
    print(f"   Game-level columns: {len(game_level_cols)}")
    print(f"   Columns to prefix: {len(cols_to_prefix)}")
    
    # Add HOME_ prefix
    home_rename = {col: f'HOME_{col}' for col in cols_to_prefix}
    home_df = home_df.rename(columns=home_rename)
    
    # Add AWAY_ prefix
    away_rename = {col: f'AWAY_{col}' for col in cols_to_prefix}
    away_df = away_df.rename(columns=away_rename)
    
    # Add NEUTRAL_VENUE flag to game-level columns (keep from first occurrence)
    if 'is_neutral' in home_df.columns:
        home_df = home_df.rename(columns={'is_neutral': 'NEUTRAL_VENUE'})
        game_level_cols_with_neutral = game_level_cols + ['NEUTRAL_VENUE']
    else:
        game_level_cols_with_neutral = game_level_cols
    
    # Select columns for merge
    home_cols = game_level_cols_with_neutral + [f'HOME_{col}' for col in cols_to_prefix]
    away_cols = game_level_cols + [f'AWAY_{col}' for col in cols_to_prefix]
    
    home_df = home_df[home_cols]
    away_df = away_df[away_cols]
    
    # ========================================================================
    # 6. MERGE HOME AND AWAY
    # ========================================================================
    print("\n6. Merging home and away data...")
    
    game_df = pd.merge(
        home_df,
        away_df,
        on=game_level_cols,
        how='inner',
        validate='1:1'
    )
    
    print(f"   ✓ Game-level rows: {len(game_df):,}")
    print(f"   ✓ Total columns: {len(game_df.columns)}")
    
    # Verify no data loss
    expected_games = df['GAME_ID'].nunique()
    actual_games = len(game_df)
    
    if actual_games == expected_games:
        print(f"   ✅ Perfect: No data loss (all {actual_games} games preserved)")
    else:
        diff = expected_games - actual_games
        print(f"   ⚠️  WARNING: Lost {diff} games in merge!")
        print(f"      Expected: {expected_games}, Got: {actual_games}")
    
    # ========================================================================
    # 7. CREATE TARGET VARIABLE
    # ========================================================================
    print("\n7. Creating target variable (HOME_WIN)...")
    
    game_df['HOME_WIN'] = (game_df['HOME_WL'] == 'W').astype(int)
    
    home_wins = game_df['HOME_WIN'].sum()
    away_wins = (1 - game_df['HOME_WIN']).sum()
    home_win_pct = game_df['HOME_WIN'].mean() * 100
    
    print(f"   ✓ Created HOME_WIN target")
    print(f"   Home wins: {home_wins:,} ({home_win_pct:.1f}%)")
    print(f"   Away wins: {away_wins:,} ({100 - home_win_pct:.1f}%)")
    
    # Analyze neutral venue games separately
    if 'NEUTRAL_VENUE' in game_df.columns and n_neutral > 0:
        neutral_games = game_df[game_df['NEUTRAL_VENUE'] == 1]
        neutral_home_wins = neutral_games['HOME_WIN'].sum()
        neutral_total = len(neutral_games)
        neutral_pct = (neutral_home_wins / neutral_total * 100) if neutral_total > 0 else 0
        
        print(f"\n   Neutral venue game results:")
        print(f"   'Home' wins: {neutral_home_wins} / {neutral_total} ({neutral_pct:.1f}%)")
        print(f"   (Note: 'home' is arbitrary for neutral venues - expect ~50%)")
    
    # ========================================================================
    # 8. SORT BY DATE
    # ========================================================================
    print("\n8. Sorting by game date...")
    
    game_df['GAME_DATE'] = pd.to_datetime(game_df['GAME_DATE'])
    game_df = game_df.sort_values('GAME_DATE').reset_index(drop=True)
    
    # ========================================================================
    # 9. DATA QUALITY CHECKS
    # ========================================================================
    print("\n9. Data quality checks...")
    
    print(f"   Unique games: {game_df['GAME_ID'].nunique():,}")
    print(f"   Date range: {game_df['GAME_DATE'].min().date()} to {game_df['GAME_DATE'].max().date()}")
    
    if 'SEASON' in game_df.columns:
        seasons = sorted(game_df['SEASON'].unique())
        print(f"   Seasons: {', '.join(seasons)}")
    
    # Duplicates
    duplicates = game_df['GAME_ID'].duplicated().sum()
    if duplicates == 0:
        print(f"   ✓ No duplicate games")
    else:
        print(f"   ⚠️  {duplicates} duplicate game IDs")
    
    # Missing values
    total_nulls = game_df.isnull().sum().sum()
    if total_nulls == 0:
        print(f"   ✓ No missing values")
    else:
        print(f"   Missing values: {total_nulls:,}")
        print(f"   (First game NaNs in _PRIOR columns are expected)")
    
    # ========================================================================
    # 10. SAVE OUTPUT
    # ========================================================================
    print(f"\n10. Saving game-level data...")
    
    game_df.to_csv(output_file, index=False)
    
    import os
    if os.path.exists(output_file):
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"   ✓ Saved to: {output_file}")
        print(f"   ✓ File size: {file_size_mb:.2f} MB")
    
    # ========================================================================
    # 11. FINAL SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    home_cols = [col for col in game_df.columns if col.startswith('HOME_')]
    away_cols = [col for col in game_df.columns if col.startswith('AWAY_')]
    
    print(f"\nInput:  {len(df):,} rows (team-level)")
    print(f"Output: {len(game_df):,} rows (game-level)")
    print(f"\nColumns: {len(home_cols)} HOME_, {len(away_cols)} AWAY_")
    print(f"Target: HOME_WIN (home win rate: {home_win_pct:.1f}%)")
    
    if 'NEUTRAL_VENUE' in game_df.columns:
        print(f"Neutral venues: {(game_df['NEUTRAL_VENUE'] == 1).sum()} games")
    
    print(f"\nData quality:")
    print(f"  ✓ No games lost: {actual_games == expected_games}")
    print(f"  ✓ No duplicates: {duplicates == 0}")
    
    print("\n" + "=" * 80)
    print("✅ STEP 3 COMPLETE!")
    print("=" * 80)
    
    print("\nNext step: Remove first games (where _PRIOR is NaN)")
    
    return game_df


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "CREATE GAME-LEVEL DATASET (CORRECT VERSION)" + " " * 18 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Configuration
    INPUT_FILE = "data/processed/nba/nba_team_game_data.csv"
    OUTPUT_FILE = "data/processed/nba/nba_game_level_data.csv"
    
    print(f"\n📁 Configuration:")
    print(f"   Input:  {INPUT_FILE}")
    print(f"   Output: {OUTPUT_FILE}")
    
    print("\n" + "=" * 80)
    print("WHY THIS VERSION IS CORRECT")
    print("=" * 80)
    print("""
This script CORRECTLY handles neutral venue games:

✅ What it does:
  1. Detects neutral venue games (both teams show @)
  2. For neutral games: Assigns first team alphabetically as "home"
  3. For regular games: Uses vs./@ as normal
  4. Preserves ALL games (no data loss)

❌ What the simplified version did wrong:
  - Ignored neutral venue games
  - Lost games where both teams showed @
  - Caused merge failures
  - Silently dropped data

Example:
  Game: LAL @ BKN (both teams show @)
  
  Simplified version:
    Both marked as away → No home team → Merge fails → GAME LOST ❌
  
  This version:
    Detects neutral → Assigns BKN as "home" (alphabetically) → Merge succeeds → GAME KEPT ✅

Result: ALL games preserved, including rare neutral venue games.
    """)
    
    try:
        df_game = create_game_level_data(INPUT_FILE, OUTPUT_FILE)
        
        print("\n✅ SUCCESS!")
        print(f"Game-level dataset: {OUTPUT_FILE}")
        print(f"Total games: {len(df_game):,}")
        
    except FileNotFoundError as e:
        print(f"\n❌ FILE NOT FOUND: {INPUT_FILE}")
        print("Please update the INPUT_FILE path")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()