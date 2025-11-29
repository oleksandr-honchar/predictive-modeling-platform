"""
NBA Feature Engineering with Proper Shifting + REST + 4F + Validation + FIXED
===============================================================================

CHANGES FROM ORIGINAL:
1. Preserves HOME_PTS and AWAY_PTS (not shifted - actual game outcomes)
2. Adds 'spread' column (HOME_PTS - AWAY_PTS)
3. Adds 'total' column (HOME_PTS + AWAY_PTS)
4. Converts all column names to lowercase at the end

Steps:
1. Load matchup-level data (1 row per game)
2. Preserve PTS columns (actual game outcomes)
3. Shift ALL team stats to make them "prior" (except PTS)
4. Calculate rolling features (L5, L10)
5. Calculate REST features (current + rolling)
6. Calculate momentum features
7. Rebuild matchup level
8. Calculate H2H features
9. Create differentials (including 4F)
10. Add spread and total columns
11. Filter Game 1
12. Reorder columns (move target variables to end)
13. Convert all columns to lowercase
14. Validate after each step
15. Save final output
"""

import pandas as pd
import numpy as np
import os

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = 'data/processed/nba/intermediate/nba_games_with_stats.csv'
OUTPUT_DIR = 'data/processed/nba/final'
OUTPUT_FILE = 'nba_train_data.csv'

# ============================================================
# UTILITIES
# ============================================================

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def validate_step(df, step_name):
    print_section(f"VALIDATION: {step_name}")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"⚠️  Missing values after {step_name}:")
        for col, cnt in missing[missing > 0].items():
            print(f"  {col}: {cnt}")
    else:
        print(f"✓ No missing values after {step_name}")
    print(f"Data shape: {df.shape}\n")
    return df

# ============================================================
# 1. LOAD AND SHIFT STATS (PRESERVE PTS)
# ============================================================

def load_and_shift_stats(filepath):
    print_section("LOADING INPUT FILE AND SHIFTING TEAM STATS")
    
    df = pd.read_csv(filepath, parse_dates=['GAME_DATE'])
    df = df.sort_values('GAME_DATE').reset_index(drop=True)
    
    print_section("INPUT FILE COLUMNS")
    for c in df.columns:
        print(f"  - {c}")
    
    # PRESERVE PTS COLUMNS (actual game outcomes - do not shift these)
    # Extract HOME_PTS and AWAY_PTS before processing
    pts_data = df[['GAME_ID', 'HOME_PTS', 'AWAY_PTS']].copy() if 'HOME_PTS' in df.columns else None
    
    # TEAM STATS (exclude identifiers AND PTS which we'll handle separately)
    exclude_keywords = ['TEAM_ID','TEAM_ABBREVIATION','TEAM_NAME','WL','HOME_WIN']
    
    # Get all stat columns (excluding PTS for now)
    home_stat_cols = [c for c in df.columns 
                      if c.startswith('HOME_') 
                      and not any(ex in c for ex in exclude_keywords)
                      and c != 'HOME_PTS']
    
    away_stat_cols = [c for c in df.columns 
                      if c.startswith('AWAY_') 
                      and not any(ex in c for ex in exclude_keywords)
                      and c != 'AWAY_PTS']
    
    # HOME team view
    home_games = df[['GAME_ID','GAME_DATE','SEASON','HOME_TEAM_ID'] + home_stat_cols].copy()
    home_games.columns = ['GAME_ID','GAME_DATE','SEASON','TEAM_ID'] + [c.replace('HOME_','') for c in home_stat_cols]
    home_games['IS_HOME'] = 1
    
    # AWAY team view
    away_games = df[['GAME_ID','GAME_DATE','SEASON','AWAY_TEAM_ID'] + away_stat_cols].copy()
    away_games.columns = ['GAME_ID','GAME_DATE','SEASON','TEAM_ID'] + [c.replace('AWAY_','') for c in away_stat_cols]
    away_games['IS_HOME'] = 0
    
    all_games = pd.concat([home_games, away_games], ignore_index=True)
    all_games = all_games.sort_values(['TEAM_ID','GAME_DATE']).reset_index(drop=True)
    
    # SHIFT ALL STATS TO PRIOR GAME (this makes them point-in-time predictors)
    stat_cols = [c for c in all_games.columns if c not in ['GAME_ID','GAME_DATE','SEASON','TEAM_ID','IS_HOME']]
    for col in stat_cols:
        all_games[col] = all_games.groupby('TEAM_ID')[col].shift(1).fillna(0)
    
    all_games = validate_step(all_games, "Shifted Team Stats")
    
    return df, all_games, pts_data

# ============================================================
# 2. ROLLING FEATURES
# ============================================================

def calculate_rolling_features(team_df):
    print_section("CALCULATING ROLLING FEATURES L5/L10 (INCLUDING 4F)")
    
    # Remove TM_ prefix from turnover
    rename_map = {'TM_TOV_PCT':'TOV_PCT'}
    for old,new in rename_map.items():
        if old in team_df.columns:
            team_df.rename(columns={old:new}, inplace=True)
    
    stats_to_roll = [
        'NET_RATING','OFF_RATING','DEF_RATING','W_PCT',
        'EFG_PCT','TOV_PCT','OREB_PCT','FTA_RATE',
        'OPP_EFG_PCT','OPP_TOV_PCT','DREB_PCT','OPP_FTA_RATE',
        'PACE','TS_PCT','AST_PCT','PIE'
    ]
    stats_to_roll = [s for s in stats_to_roll if s in team_df.columns]
    
    for stat in stats_to_roll:
        for window in [5,10]:
            team_df[f'{stat}_L{window}'] = (
                team_df.groupby('TEAM_ID')[stat]
                .rolling(window,min_periods=1)
                .mean()
                .reset_index(level=0,drop=True)
                .fillna(0)
            )
    
    team_df = validate_step(team_df, "Rolling Features")
    return team_df

# ============================================================
# 3. REST FEATURES
# ============================================================

def calculate_rest_features(team_df):
    print_section("CALCULATING REST FEATURES")
    
    df = team_df.copy().sort_values(['TEAM_ID','GAME_DATE']).reset_index(drop=True)
    
    df['DAYS_REST'] = df.groupby('TEAM_ID')['GAME_DATE'].diff().dt.days.fillna(3)
    df['B2B'] = (df['DAYS_REST']==1).astype(int)
    df['OPTIMAL_REST'] = ((df['DAYS_REST']>=2)&(df['DAYS_REST']<=3)).astype(int)
    df['OVER_RESTED'] = (df['DAYS_REST']>=4).astype(int)
    
    # Rolling REST
    df['B2B_IN_L5'] = df.groupby('TEAM_ID')['B2B'].rolling(5,min_periods=1).sum().reset_index(level=0,drop=True).shift(1).fillna(0)
    df['B2B_IN_L10'] = df.groupby('TEAM_ID')['B2B'].rolling(10,min_periods=1).sum().reset_index(level=0,drop=True).shift(1).fillna(0)
    df['AVG_REST_L10'] = df.groupby('TEAM_ID')['DAYS_REST'].rolling(10,min_periods=1).mean().reset_index(level=0,drop=True).shift(1).fillna(2.5)
    
    df = validate_step(df, "REST Features")
    return df

# ============================================================
# 4. MOMENTUM FEATURES
# ============================================================

def calculate_momentum(team_df):
    print_section("CALCULATING MOMENTUM FEATURES")
    
    if 'W_PCT_L5' in team_df.columns and 'W_PCT_L10' in team_df.columns:
        team_df['MOMENTUM'] = (team_df['W_PCT_L5'] - team_df['W_PCT_L10']).fillna(0)
    
    if 'W_PCT' in team_df.columns:
        team_df['WIN_INDICATOR'] = (team_df['W_PCT'] > team_df.groupby('TEAM_ID')['W_PCT'].shift(1)).astype(int)
        
        def streak_count(s):
            s=s.fillna(0)
            groups = (s!=s.shift()).cumsum()
            streaks = s.groupby(groups).cumcount()+1
            return (s*streaks).fillna(0)
        
        team_df['WIN_STREAK'] = team_df.groupby('TEAM_ID')['WIN_INDICATOR'].apply(streak_count).reset_index(level=0,drop=True)
        team_df.drop(columns=['WIN_INDICATOR'], inplace=True)
    
    team_df = validate_step(team_df, "Momentum Features")
    return team_df

# ============================================================
# 5. REBUILD MATCHUP LEVEL
# ============================================================

def rebuild_matchup_level(team_df, original_df, pts_data):
    print_section("REBUILDING MATCHUP LEVEL")
    
    home = team_df[team_df['IS_HOME']==1].copy().set_index('GAME_ID')
    away = team_df[team_df['IS_HOME']==0].copy().set_index('GAME_ID')
    
    # Exclude base identifiers
    base_cols = ['GAME_ID','GAME_DATE','SEASON','HOME_TEAM_ID','HOME_TEAM_ABBREVIATION','HOME_TEAM_NAME',
                 'AWAY_TEAM_ID','AWAY_TEAM_ABBREVIATION','AWAY_TEAM_NAME','HOME_WIN']
    base = original_df[base_cols].copy().set_index('GAME_ID')
    
    # Only include team stats (exclude any ID/name columns) for prefixing
    exclude_cols = ['GAME_ID','GAME_DATE','SEASON','TEAM_ID','IS_HOME','HOME_WIN']
    
    home_stats = [c for c in home.columns if c not in exclude_cols]
    away_stats = [c for c in away.columns if c not in exclude_cols]
    
    home_prefixed = home[home_stats].add_prefix('HOME_')
    away_prefixed = away[away_stats].add_prefix('AWAY_')
    
    # Join safely (no overlapping columns)
    matchup = base.join(home_prefixed, how='inner').join(away_prefixed, how='inner').reset_index()
    
    # ADD BACK PTS COLUMNS (these are actual game outcomes, not shifted)
    if pts_data is not None:
        matchup = matchup.merge(pts_data, on='GAME_ID', how='left')
        print("✓ Added HOME_PTS and AWAY_PTS columns (actual game outcomes)")
    
    matchup = validate_step(matchup, "Matchup-level Rebuild")
    return matchup


# ============================================================
# 6. H2H FEATURES
# ============================================================

def calculate_h2h(df):
    print_section("CALCULATING HEAD-TO-HEAD FEATURES")
    
    df = df.sort_values('GAME_DATE').reset_index(drop=True)
    df['MATCHUP_ID'] = df.apply(lambda r: tuple(sorted([r['HOME_TEAM_ID'], r['AWAY_TEAM_ID']])), axis=1)
    df['TEAM_A'] = df['MATCHUP_ID'].apply(lambda m: m[0])
    df['TEAM_A_WON'] = np.where(df['HOME_TEAM_ID']==df['TEAM_A'], df['HOME_WIN'], 1-df['HOME_WIN'])
    
    df['PRIOR_A_WINS'] = df.groupby('MATCHUP_ID')['TEAM_A_WON'].cumsum().shift(1).fillna(0)
    df['H2H_GAMES'] = df.groupby('MATCHUP_ID').cumcount()
    df['H2H_HOME_WINS'] = np.where(df['HOME_TEAM_ID']==df['TEAM_A'], df['PRIOR_A_WINS'], df['H2H_GAMES']-df['PRIOR_A_WINS'])
    df['H2H_HOME_WIN_PCT'] = np.where(df['H2H_GAMES']>0, df['H2H_HOME_WINS']/df['H2H_GAMES'],0.5)
    
    df.drop(columns=['MATCHUP_ID','TEAM_A','TEAM_A_WON','PRIOR_A_WINS'], inplace=True)
    df = validate_step(df, "H2H Features")
    return df

# ============================================================
# 7. DIFFERENTIALS INCLUDING 4F
# ============================================================

def create_differentials(df):
    print_section("CREATING DIFFERENTIALS (INCLUDING 4F)")
    
    # REST advantage and B2B
    if 'HOME_DAYS_REST' in df.columns and 'AWAY_DAYS_REST' in df.columns:
        df['REST_ADVANTAGE'] = df['HOME_DAYS_REST'] - df['AWAY_DAYS_REST']
    if 'HOME_B2B' in df.columns and 'AWAY_B2B' in df.columns:
        df['B2B_DIFF'] = df['HOME_B2B'] - df['AWAY_B2B']
    
    # All overlapping columns
    home_features = [c.replace('HOME_','') for c in df.columns if c.startswith('HOME_')]
    away_features = [c.replace('AWAY_','') for c in df.columns if c.startswith('AWAY_')]
    common_features = set(home_features) & set(away_features)
    
    # Exclude identifiers, raw box score stats, and PTS (we'll handle PTS separately for spread/total)
    exclude = ['TEAM_ID','TEAM_ABBREVIATION','TEAM_NAME','WL','PTS','FGM','FGA','FG3M','FG3A','FTM','FTA',
               'OREB','DREB','REB','AST','STL','BLK','TOV','PF','PLUS_MINUS','DAYS_REST','B2B']
    
    for f in [x for x in common_features if x not in exclude]:
        df[f'{f}_DIFF'] = (df[f'HOME_{f}'] - df[f'AWAY_{f}']).fillna(0)
    
    df = validate_step(df, "Differentials")
    return df

# ============================================================
# 8. ADD SPREAD AND TOTAL
# ============================================================

def add_spread_and_total(df):
    print_section("ADDING SPREAD AND TOTAL COLUMNS")
    
    if 'HOME_PTS' in df.columns and 'AWAY_PTS' in df.columns:
        df['SPREAD'] = df['HOME_PTS'] - df['AWAY_PTS']
        df['TOTAL'] = df['HOME_PTS'] + df['AWAY_PTS']
        print("✓ Added SPREAD (HOME_PTS - AWAY_PTS)")
        print("✓ Added TOTAL (HOME_PTS + AWAY_PTS)")
    else:
        print("⚠️  HOME_PTS or AWAY_PTS not found - cannot create SPREAD and TOTAL")
    
    df = validate_step(df, "Spread and Total")
    return df

# ============================================================
# 9. FILTER GAME 1
# ============================================================

def filter_game_1(df):
    print_section("FILTERING FIRST GAME OF SEASON")
    df = df.sort_values(['SEASON','HOME_TEAM_ID','GAME_DATE']).reset_index(drop=True)
    df['GAME_NUM'] = df.groupby(['SEASON','HOME_TEAM_ID']).cumcount()+1
    df_filtered = df[df['GAME_NUM']>1].copy().drop(columns=['GAME_NUM'])
    df_filtered = validate_step(df_filtered, "Filter Game 1")
    return df_filtered

# ============================================================
# 10. REORDER TARGET VARIABLES
# ============================================================

def reorder_target_variables(df):
    print_section("REORDERING TARGET VARIABLES TO END")
    
    # Target variables to move to the end
    target_vars = ['HOME_WIN', 'HOME_PTS', 'AWAY_PTS', 'SPREAD', 'TOTAL']
    
    # Get columns that exist in the dataframe
    existing_targets = [col for col in target_vars if col in df.columns]
    
    # Get all other columns
    other_cols = [col for col in df.columns if col not in existing_targets]
    
    # Reorder: other columns first, then targets
    df = df[other_cols + existing_targets]
    
    print(f"✓ Moved {len(existing_targets)} target variables to end: {existing_targets}")
    return df

# ============================================================
# 11. CONVERT TO LOWERCASE
# ============================================================

def convert_to_lowercase(df):
    print_section("CONVERTING ALL COLUMN NAMES TO LOWERCASE")
    original_cols = df.columns.tolist()
    df.columns = [c.lower() for c in df.columns]
    print(f"✓ Converted {len(df.columns)} column names to lowercase")
    return df

# ============================================================
# 12. FINAL COLUMN CHECK
# ============================================================

def print_all_columns(df):
    print_section("FINAL COLUMN CHECK")
    print(f"Total columns: {len(df.columns)}\n")
    print("Column names:")
    for col in df.columns:
        print(f"  - {col}")

# ============================================================
# 13. MAIN
# ============================================================

def main(input_path, output_path):
    original_df, team_df, pts_data = load_and_shift_stats(input_path)
    team_df = calculate_rolling_features(team_df)
    team_df = calculate_rest_features(team_df)
    team_df = calculate_momentum(team_df)
    
    matchup_df = rebuild_matchup_level(team_df, original_df, pts_data)
    matchup_df = calculate_h2h(matchup_df)
    final_df = create_differentials(matchup_df)
    final_df = add_spread_and_total(final_df)
    final_df = filter_game_1(final_df)
    final_df = reorder_target_variables(final_df)
    final_df = convert_to_lowercase(final_df)
    
    print_all_columns(final_df)
    
    # Summary statistics
    print_section("SUMMARY STATISTICS")
    if 'home_pts' in final_df.columns and 'away_pts' in final_df.columns:
        print(f"HOME_PTS range: {final_df['home_pts'].min():.1f} - {final_df['home_pts'].max():.1f}")
        print(f"AWAY_PTS range: {final_df['away_pts'].min():.1f} - {final_df['away_pts'].max():.1f}")
    if 'spread' in final_df.columns:
        print(f"SPREAD range: {final_df['spread'].min():.1f} - {final_df['spread'].max():.1f}")
        print(f"SPREAD mean: {final_df['spread'].mean():.2f} (should be positive, home advantage)")
    if 'total' in final_df.columns:
        print(f"TOTAL range: {final_df['total'].min():.1f} - {final_df['total'].max():.1f}")
        print(f"TOTAL mean: {final_df['total'].mean():.1f}")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved final dataset to {output_path}\n")
    
    return final_df

if __name__ == "__main__":
    main(INPUT_FILE, os.path.join(OUTPUT_DIR, OUTPUT_FILE))