"""
Merge Games with Team Stats - Clean Version
============================================

Merges game data with team advanced statistics.
Stats are AS OF game date (will be lagged later in feature engineering).

Features:
- No _PRIOR suffix (lagging happens in feature engineering)
- Logical column grouping (Four Factors together, etc.)
- Removes useless columns (_RANK, STAT_TYPE)
- Clean, organized output

INPUT:
    data/raw/nba/nba_games_all_seasons_RAW.csv
    data/raw/nba/nba_team_stats_by_date.csv

OUTPUT:
    data/processed/nba/nba_games_with_stats.csv
"""

import pandas as pd
import os

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_GAMES = 'data/raw/nba/nba_games_all_seasons_RAW.csv'
INPUT_STATS = 'data/raw/nba/nba_team_stats_by_date.csv'
OUTPUT_DIR = 'data/processed/nba'
OUTPUT_FILE = 'nba_games_with_stats.csv'

# ============================================================
# COLUMN DEFINITIONS
# ============================================================

# Columns to keep from stats (organized by category)
STAT_COLUMNS = {
    'basic': [
        'GP', 'W', 'L', 'W_PCT', 'MIN'
    ],
    
    'advanced': [
        'OFF_RATING', 'DEF_RATING', 'NET_RATING',
        'E_OFF_RATING', 'E_DEF_RATING', 'E_NET_RATING'
    ],
    
    'pace': [
        'PACE', 'E_PACE', 'PACE_PER40', 'POSS'
    ],
    
    'four_factors_offense': [
        'EFG_PCT',           # Shooting efficiency
        'TM_TOV_PCT',        # Turnovers
        'OREB_PCT',          # Offensive rebounds
        'FTA_RATE'           # Free throw rate
    ],
    
    'four_factors_defense': [
        'OPP_EFG_PCT',       # Opponent shooting
        'OPP_TOV_PCT',       # Opponent turnovers
        'DREB_PCT',          # Defensive rebounds (inverse of OPP_OREB_PCT)
        'OPP_FTA_RATE'       # Opponent free throws
    ],
    
    'other_offense': [
        'AST_PCT', 'AST_TO', 'AST_RATIO', 'TS_PCT'
    ],
    
    'other_defense': [
        'REB_PCT', 'OREB_PCT_FF'
    ],
    
    'misc': [
        'PIE', 'PLUS_MINUS'
    ]
}

# Flatten to single list
ALL_STAT_COLS = []
for category in STAT_COLUMNS.values():
    ALL_STAT_COLS.extend(category)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_stats_dataframe(stats_df):
    """
    Clean stats dataframe: remove ranks, STAT_TYPE, etc.
    
    Args:
        stats_df: Raw stats from collection script
    
    Returns:
        Cleaned stats dataframe
    """
    print("\nCleaning stats dataframe...")
    
    # Remove _RANK columns (useless for modeling)
    rank_cols = [col for col in stats_df.columns if col.endswith('_RANK')]
    if rank_cols:
        stats_df = stats_df.drop(columns=rank_cols)
        print(f"  ✓ Removed {len(rank_cols)} _RANK columns")
    
    # Remove STAT_TYPE column (all 'Advanced')
    if 'STAT_TYPE' in stats_df.columns:
        stats_df = stats_df.drop(columns=['STAT_TYPE'])
        print(f"  ✓ Removed STAT_TYPE column")
    
    # Keep only columns we need
    keep_cols = ['TEAM_ID', 'TEAM_NAME', 'GAME_DATE', 'SEASON'] + [
        col for col in ALL_STAT_COLS if col in stats_df.columns
    ]
    
    missing_cols = [col for col in ALL_STAT_COLS if col not in stats_df.columns]
    if missing_cols:
        print(f"\n  ⚠️  Missing columns: {', '.join(missing_cols[:5])}")
        if len(missing_cols) > 5:
            print(f"     ... and {len(missing_cols) - 5} more")
    
    stats_df = stats_df[keep_cols]
    print(f"  ✓ Kept {len(stats_df.columns)} useful columns")
    
    return stats_df


def merge_team_stats(games_df, stats_df, team_prefix):
    """
    Merge team stats with games for HOME or AWAY team.
    
    Args:
        games_df: Game data
        stats_df: Cleaned stats data
        team_prefix: 'HOME' or 'AWAY'
    
    Returns:
        Games dataframe with team stats added
    """
    print(f"\nMerging {team_prefix} team stats...")
    
    team_id_col = f'{team_prefix}_TEAM_ID'
    
    # Merge
    merged = games_df.merge(
        stats_df,
        left_on=[team_id_col, 'GAME_DATE', 'SEASON'],
        right_on=['TEAM_ID', 'GAME_DATE', 'SEASON'],
        how='left',
        suffixes=('', '_DROP')
    )
    
    # Rename stat columns with prefix (no _PRIOR suffix!)
    for col in ALL_STAT_COLS:
        if col in merged.columns:
            merged[f'{team_prefix}_{col}'] = merged[col]
    
    # Drop temporary columns
    drop_cols = ['TEAM_ID', 'TEAM_NAME'] + [
        col for col in merged.columns 
        if col.endswith('_DROP') or col in ALL_STAT_COLS
    ]
    merged = merged.drop(columns=[col for col in drop_cols if col in merged.columns])
    
    # Count successful merges
    new_cols = [col for col in merged.columns if col.startswith(f'{team_prefix}_') and col != team_id_col]
    successful = merged[new_cols[0]].notna().sum() if new_cols else 0
    
    print(f"  ✓ Added {len(new_cols)} stat columns")
    print(f"  ✓ Successful merges: {successful:,} / {len(merged):,} ({successful/len(merged)*100:.1f}%)")
    
    return merged


def organize_columns(df):
    """
    Organize columns in logical order.
    
    Order:
    1. Game identifiers (GAME_ID, GAME_DATE, SEASON)
    2. Team identifiers (HOME/AWAY TEAM_ID, ABBREVIATION, NAME)
    3. Game result (HOME_WIN, scores)
    4. Game stats (box score)
    5. HOME advanced stats (grouped logically)
    6. AWAY advanced stats (grouped logically)
    """
    print("\nOrganizing columns...")
    
    # Define column order
    ordered_cols = []
    
    # 1. Game identifiers
    game_id_cols = ['GAME_ID', 'GAME_DATE', 'SEASON']
    ordered_cols.extend([col for col in game_id_cols if col in df.columns])
    
    # 2. Team identifiers
    team_id_cols = [
        'HOME_TEAM_ID', 'HOME_TEAM_ABBREVIATION', 'HOME_TEAM_NAME',
        'AWAY_TEAM_ID', 'AWAY_TEAM_ABBREVIATION', 'AWAY_TEAM_NAME'
    ]
    ordered_cols.extend([col for col in team_id_cols if col in df.columns])
    
    # 3. Game result
    result_cols = ['HOME_WIN', 'HOME_WL', 'AWAY_WL', 'HOME_PTS', 'AWAY_PTS', 'HOME_PLUS_MINUS', 'AWAY_PLUS_MINUS']
    ordered_cols.extend([col for col in result_cols if col in df.columns])
    
    # 4. Game stats (box score)
    box_score_cols = [col for col in df.columns if any(x in col for x in ['FGM', 'FGA', 'FG_PCT', 'FG3', 'FTM', 'FTA', 'FT_PCT', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF']) and not any(x in col for x in ['_RATING', '_PCT_FF', 'AST_TO', 'AST_RATIO'])]
    ordered_cols.extend([col for col in box_score_cols if col not in ordered_cols])
    
    # 5. HOME advanced stats (in logical groups)
    for team_prefix in ['HOME', 'AWAY']:
        # Basic
        for col in STAT_COLUMNS['basic']:
            full_col = f'{team_prefix}_{col}'
            if full_col in df.columns and full_col not in ordered_cols:
                ordered_cols.append(full_col)
        
        # Advanced ratings
        for col in STAT_COLUMNS['advanced']:
            full_col = f'{team_prefix}_{col}'
            if full_col in df.columns and full_col not in ordered_cols:
                ordered_cols.append(full_col)
        
        # Pace
        for col in STAT_COLUMNS['pace']:
            full_col = f'{team_prefix}_{col}'
            if full_col in df.columns and full_col not in ordered_cols:
                ordered_cols.append(full_col)
        
        # Four Factors - Offense (TOGETHER!)
        for col in STAT_COLUMNS['four_factors_offense']:
            full_col = f'{team_prefix}_{col}'
            if full_col in df.columns and full_col not in ordered_cols:
                ordered_cols.append(full_col)
        
        # Four Factors - Defense (TOGETHER!)
        for col in STAT_COLUMNS['four_factors_defense']:
            full_col = f'{team_prefix}_{col}'
            if full_col in df.columns and full_col not in ordered_cols:
                ordered_cols.append(full_col)
        
        # Other offensive stats
        for col in STAT_COLUMNS['other_offense']:
            full_col = f'{team_prefix}_{col}'
            if full_col in df.columns and full_col not in ordered_cols:
                ordered_cols.append(full_col)
        
        # Other defensive stats
        for col in STAT_COLUMNS['other_defense']:
            full_col = f'{team_prefix}_{col}'
            if full_col in df.columns and full_col not in ordered_cols:
                ordered_cols.append(full_col)
        
        # Misc
        for col in STAT_COLUMNS['misc']:
            full_col = f'{team_prefix}_{col}'
            if full_col in df.columns and full_col not in ordered_cols:
                ordered_cols.append(full_col)
    
    # Add any remaining columns
    remaining = [col for col in df.columns if col not in ordered_cols]
    if remaining:
        print(f"  ⚠️  {len(remaining)} columns not in predefined order (adding at end)")
        ordered_cols.extend(remaining)
    
    df = df[ordered_cols]
    
    print(f"  ✓ Organized {len(df.columns)} columns")
    
    return df


# ============================================================
# MAIN
# ============================================================

def main():
    """Main merge workflow."""
    print("\n" + "="*70)
    print("MERGE GAMES WITH TEAM STATISTICS")
    print("="*70)
    print("\nFeatures:")
    print("  ✓ No _PRIOR suffix (lagging happens in feature engineering)")
    print("  ✓ Four Factors grouped together (4 offensive + 4 defensive)")
    print("  ✓ Removed _RANK columns (useless for modeling)")
    print("  ✓ Removed STAT_TYPE column (all 'Advanced')")
    print("  ✓ Logical column ordering")
    
    # Load data
    print("\n[STEP 1] Loading data...")
    
    if not os.path.exists(INPUT_GAMES):
        print(f"✗ Error: {INPUT_GAMES} not found!")
        print("  Run collect_nba_games_improved.py first")
        return
    
    if not os.path.exists(INPUT_STATS):
        print(f"✗ Error: {INPUT_STATS} not found!")
        print("  Run collect_team_stats_improved.py first")
        return
    
    games = pd.read_csv(INPUT_GAMES, parse_dates=['GAME_DATE'])
    stats = pd.read_csv(INPUT_STATS, parse_dates=['GAME_DATE'])
    
    print(f"✓ Games: {len(games):,} rows, {len(games.columns)} columns")
    print(f"✓ Stats: {len(stats):,} rows, {len(stats.columns)} columns")
    print(f"  Date range: {games['GAME_DATE'].min().date()} to {games['GAME_DATE'].max().date()}")
    
    # Clean stats
    print("\n[STEP 2] Cleaning stats dataframe...")
    stats = clean_stats_dataframe(stats)
    
    # Merge HOME team stats
    print("\n[STEP 3] Merging HOME team stats...")
    games = merge_team_stats(games, stats, 'HOME')
    
    # Merge AWAY team stats
    print("\n[STEP 4] Merging AWAY team stats...")
    games = merge_team_stats(games, stats, 'AWAY')
    
    # Organize columns
    print("\n[STEP 5] Organizing columns...")
    games = organize_columns(games)
    
    # Show Four Factors grouping
    print("\n✓ Four Factors columns (grouped together):")
    ff_cols = [col for col in games.columns if any(ff in col for ff in ['EFG_PCT', 'TM_TOV_PCT', 'OREB_PCT', 'FTA_RATE', 'OPP_EFG_PCT', 'OPP_TOV_PCT', 'DREB_PCT', 'OPP_FTA_RATE']) and '_FF' not in col]
    for i, col in enumerate(ff_cols, 1):
        print(f"  {i}. {col}")
    
    # Save
    print("\n[STEP 6] Saving...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    games.to_csv(output_path, index=False)
    
    # Summary
    print("\n" + "="*70)
    print("✓ MERGE COMPLETE")
    print("="*70)
    print(f"Output: {output_path}")
    print(f"Rows: {len(games):,}")
    print(f"Columns: {len(games.columns)}")
    
    # Missing value check
    missing = games.isnull().sum()
    cols_with_missing = missing[missing > 0]
    
    if len(cols_with_missing) > 0:
        print(f"\n⚠️  Columns with missing values: {len(cols_with_missing)}")
        print("  (This is expected for Game 1 of each season)")
        for col, count in cols_with_missing.head(5).items():
            pct = count / len(games) * 100
            print(f"    {col}: {count} ({pct:.1f}%)")
        if len(cols_with_missing) > 5:
            print(f"    ... and {len(cols_with_missing) - 5} more")
    else:
        print("\n✓ No missing values!")
    
    # Show column structure
    print("\n📋 Column structure:")
    print("  Game identifiers: GAME_ID, GAME_DATE, SEASON")
    print("  Team identifiers: HOME/AWAY_TEAM_ID, _ABBREVIATION, _NAME")
    print("  Game results: HOME_WIN, scores, plus/minus")
    print("  Box score stats: FG, 3P, FT, rebounds, assists, etc.")
    print("  HOME advanced stats:")
    print("    - Basic: GP, W, L, W_PCT, MIN")
    print("    - Ratings: OFF_RATING, DEF_RATING, NET_RATING")
    print("    - Four Factors Offense: EFG_PCT, TM_TOV_PCT, OREB_PCT, FTA_RATE")
    print("    - Four Factors Defense: OPP_EFG_PCT, OPP_TOV_PCT, DREB_PCT, OPP_FTA_RATE")
    print("    - Other: AST_PCT, TS_PCT, PACE, etc.")
    print("  AWAY advanced stats: (same structure)")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. ✓ You now have games merged with team stats")
    print("2. → Next: Run feature engineering (will apply shift/lag)")
    print("3. → Then: Filter early games")
    print("4. → Finally: Train model")
    print("="*70)


if __name__ == "__main__":
    main()