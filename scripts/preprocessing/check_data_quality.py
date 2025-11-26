"""
Comprehensive Data Quality Checker
Run this on your nba_team_game_data.csv to find all issues
"""

import pandas as pd
import numpy as np
import sys

def check_data_quality(file_path):
    """
    Comprehensive data quality check for NBA team game data.
    
    Args:
        file_path: Path to CSV file to check
    """
    
    print("=" * 80)
    print("COMPREHENSIVE DATA QUALITY CHECK")
    print("=" * 80)
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"\n❌ ERROR: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"\n❌ ERROR loading file: {e}")
        return None
    
    print(f"\n✓ Loaded file: {file_path}")
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    
    # ========================================================================
    # 1. BASIC STRUCTURE CHECK
    # ========================================================================
    print("\n" + "=" * 80)
    print("1. BASIC STRUCTURE")
    print("=" * 80)
    
    required_cols = ['GAME_ID', 'TEAM_ID', 'GAME_DATE', 'MATCHUP', 'WL']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"\n❌ Missing required columns: {missing_cols}")
        return None
    else:
        print("\n✓ All required columns present")
    
    print(f"\n  Unique GAME_IDs: {df['GAME_ID'].nunique():,}")
    print(f"  Unique TEAM_IDs: {df['TEAM_ID'].nunique()}")
    print(f"  Expected structure: 2 rows per game")
    
    # ========================================================================
    # 2. GAME_ID DISTRIBUTION
    # ========================================================================
    print("\n" + "=" * 80)
    print("2. GAME_ID DISTRIBUTION")
    print("=" * 80)
    
    game_counts = df['GAME_ID'].value_counts()
    
    games_with_2 = (game_counts == 2).sum()
    games_with_1 = (game_counts == 1).sum()
    games_with_more = (game_counts > 2).sum()
    
    print(f"\n  Games with exactly 2 rows: {games_with_2:,} ✓")
    
    if games_with_1 > 0:
        print(f"  Games with only 1 row: {games_with_1:,} ❌")
        print("\n  Sample incomplete games:")
        for game_id in game_counts[game_counts == 1].index[:5]:
            sample = df[df['GAME_ID'] == game_id][['GAME_ID', 'GAME_DATE', 
                                                     'TEAM_ABBREVIATION', 'MATCHUP']]
            print(f"\n{sample.to_string(index=False)}")
    
    if games_with_more > 0:
        print(f"  Games with >2 rows: {games_with_more:,} ❌")
        print("\n  Sample duplicate games:")
        for game_id in game_counts[game_counts > 2].index[:3]:
            sample = df[df['GAME_ID'] == game_id][['GAME_ID', 'GAME_DATE', 
                                                     'TEAM_ABBREVIATION', 'MATCHUP', 'WL', 'PTS']]
            print(f"\n{sample.to_string(index=False)}")
    
    # ========================================================================
    # 3. HOME/AWAY BALANCE
    # ========================================================================
    print("\n" + "=" * 80)
    print("3. HOME/AWAY BALANCE")
    print("=" * 80)
    
    df['IS_HOME'] = df['MATCHUP'].str.contains('vs.').astype(int)
    
    home_count = df['IS_HOME'].sum()
    away_count = (1 - df['IS_HOME']).sum()
    
    print(f"\n  Home games (vs.): {home_count:,}")
    print(f"  Away games (@):   {away_count:,}")
    
    if home_count == away_count:
        print("  ✓ Balanced")
    else:
        diff = abs(home_count - away_count)
        print(f"  ❌ IMBALANCED by {diff} rows!")
    
    # Check each game's home/away composition
    game_home_away = df.groupby('GAME_ID')['IS_HOME'].agg(['sum', 'count'])
    
    # Perfect games: sum=1 (one home, one away), count=2 (two teams)
    perfect_games = game_home_away[(game_home_away['sum'] == 1) & 
                                   (game_home_away['count'] == 2)]
    
    both_home = game_home_away[(game_home_away['sum'] == 2) & 
                               (game_home_away['count'] == 2)]
    
    both_away = game_home_away[(game_home_away['sum'] == 0) & 
                               (game_home_away['count'] == 2)]
    
    print(f"\n  Games with proper home/away split: {len(perfect_games):,} ✓")
    
    if len(both_home) > 0:
        print(f"  Games where BOTH teams are marked HOME: {len(both_home):,} ❌")
        print("\n  Sample (both home):")
        for game_id in list(both_home.index)[:3]:
            sample = df[df['GAME_ID'] == game_id][['GAME_ID', 'TEAM_ABBREVIATION', 'MATCHUP']]
            print(f"\n{sample.to_string(index=False)}")
    
    if len(both_away) > 0:
        print(f"  Games where BOTH teams are marked AWAY: {len(both_away):,} ❌")
        print("\n  Sample (both away):")
        for game_id in list(both_away.index)[:3]:
            sample = df[df['GAME_ID'] == game_id][['GAME_ID', 'TEAM_ABBREVIATION', 'MATCHUP']]
            print(f"\n{sample.to_string(index=False)}")
    
    # ========================================================================
    # 4. WIN/LOSS CONSISTENCY
    # ========================================================================
    print("\n" + "=" * 80)
    print("4. WIN/LOSS CONSISTENCY")
    print("=" * 80)
    
    # Check games with exactly 2 rows
    games_with_2_rows = game_counts[game_counts == 2].index
    
    wl_issues = []
    for game_id in games_with_2_rows[:1000]:  # Check first 1000
        game_data = df[df['GAME_ID'] == game_id]
        wl = game_data['WL'].tolist()
        
        if wl.count('W') != 1 or wl.count('L') != 1:
            wl_issues.append(game_id)
    
    if wl_issues:
        print(f"\n  ❌ Games with W/L issues: {len(wl_issues)}")
        print("\n  Sample:")
        for game_id in wl_issues[:3]:
            sample = df[df['GAME_ID'] == game_id][['GAME_ID', 'TEAM_ABBREVIATION', 
                                                     'WL', 'PTS', 'PLUS_MINUS']]
            print(f"\n{sample.to_string(index=False)}")
    else:
        print("\n  ✓ All checked games have proper W/L distribution")
    
    # ========================================================================
    # 5. DATE CONSISTENCY
    # ========================================================================
    print("\n" + "=" * 80)
    print("5. DATE CONSISTENCY")
    print("=" * 80)
    
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    
    date_issues = []
    for game_id in games_with_2_rows[:1000]:
        game_data = df[df['GAME_ID'] == game_id]
        if game_data['GAME_DATE'].nunique() > 1:
            date_issues.append(game_id)
    
    if date_issues:
        print(f"\n  ❌ Games with multiple dates: {len(date_issues)}")
        for game_id in date_issues[:3]:
            sample = df[df['GAME_ID'] == game_id][['GAME_ID', 'GAME_DATE', 'TEAM_ABBREVIATION']]
            print(f"\n{sample.to_string(index=False)}")
    else:
        print("\n  ✓ All games have consistent dates")
    
    # ========================================================================
    # 6. NULL VALUES
    # ========================================================================
    print("\n" + "=" * 80)
    print("6. NULL VALUES IN KEY COLUMNS")
    print("=" * 80)
    
    key_cols = ['GAME_ID', 'TEAM_ID', 'GAME_DATE', 'MATCHUP', 'WL', 
                'TEAM_ABBREVIATION', 'TEAM_NAME']
    
    has_nulls = False
    for col in key_cols:
        if col in df.columns:
            nulls = df[col].isnull().sum()
            if nulls > 0:
                print(f"  ❌ {col}: {nulls:,} null values")
                has_nulls = True
    
    if not has_nulls:
        print("\n  ✓ No null values in key columns")
    
    # ========================================================================
    # 7. EXACT DUPLICATES
    # ========================================================================
    print("\n" + "=" * 80)
    print("7. EXACT DUPLICATE ROWS")
    print("=" * 80)
    
    duplicates = df.duplicated(keep=False)
    dup_count = duplicates.sum()
    
    if dup_count > 0:
        print(f"\n  ❌ Found {dup_count:,} exact duplicate rows")
        print("\n  Sample:")
        print(df[duplicates].head(4)[['GAME_ID', 'TEAM_ABBREVIATION', 
                                       'GAME_DATE', 'WL', 'PTS']].to_string())
    else:
        print("\n  ✓ No exact duplicate rows")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY OF ISSUES")
    print("=" * 80)
    
    issues = []
    
    if games_with_1 > 0:
        issues.append(f"❌ {games_with_1:,} incomplete games (only 1 team)")
    if games_with_more > 0:
        issues.append(f"❌ {games_with_more:,} games with >2 rows")
    if home_count != away_count:
        issues.append(f"❌ Home/away imbalance: {home_count} vs {away_count}")
    if len(both_home) > 0:
        issues.append(f"❌ {len(both_home):,} games with both teams marked home")
    if len(both_away) > 0:
        issues.append(f"❌ {len(both_away):,} games with both teams marked away")
    if wl_issues:
        issues.append(f"❌ {len(wl_issues):,} games with W/L issues")
    if date_issues:
        issues.append(f"❌ {len(date_issues):,} games with date mismatches")
    if dup_count > 0:
        issues.append(f"❌ {dup_count:,} exact duplicate rows")
    
    if issues:
        print("\n⚠️  ISSUES FOUND:\n")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n📋 RECOMMENDATIONS:")
        print("\n  1. Use the FIXED script: 03_create_game_level_FIXED.py")
        print("     → Handles incomplete games and duplicates")
        print("     → Excludes problematic games automatically")
        
        print(f"\n  2. Expected output: ~{len(perfect_games):,} valid games")
        print(f"     (vs {df['GAME_ID'].nunique():,} total games in file)")
        
        affected_pct = ((df['GAME_ID'].nunique() - len(perfect_games)) / 
                       df['GAME_ID'].nunique() * 100)
        print(f"\n  3. Impact: {affected_pct:.1f}% of games affected")
        
    else:
        print("\n✅ NO ISSUES FOUND!")
        print("  Your data looks clean and ready for processing.")
    
    print("\n" + "=" * 80)
    
    return df


if __name__ == "__main__":
    
    # Default file path
    FILE_PATH = "data/processed/nba/nba_team_game_data.csv"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        FILE_PATH = sys.argv[1]
    
    print(f"\nChecking file: {FILE_PATH}\n")
    
    df = check_data_quality(FILE_PATH)
    
    if df is not None:
        print("\n✅ Data quality check complete!")
    else:
        print("\n❌ Data quality check failed!")