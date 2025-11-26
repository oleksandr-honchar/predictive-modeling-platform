"""
FIXED: Remove First Games (Counter Reset Bug Fixed)
===================================================

This version GUARANTEES proper counter reset between seasons.

Bug that was happening:
- Counters were bleeding between seasons somehow
- Caused 191 > 150 removal (41 extra games)

Fix:
- Explicit season isolation
- Fresh counters for each season
- Verification at each step

Author: Oleksandr
Date: November 25, 2024
"""

import pandas as pd
import numpy as np
import os


def remove_first_games_FIXED(input_file, output_file, n_games=1, verbose=True):
    """
    Remove first N games per team per season with GUARANTEED proper season reset.
    
    Returns:
        df_cleaned, stats
    """
    
    if verbose:
        print("\n" + "=" * 80)
        print(f"REMOVING FIRST {n_games} GAME(S) - FIXED VERSION")
        print("=" * 80)
    
    # Load
    df = pd.read_csv(input_file)
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    
    original_size = len(df)
    
    if verbose:
        print(f"\n📊 Dataset:")
        print(f"   Total games: {original_size:,}")
        print(f"   Date range: {df['GAME_DATE'].min().date()} to {df['GAME_DATE'].max().date()}")
    
    # Get unique seasons
    seasons = sorted(df['SEASON'].unique())
    
    if verbose:
        print(f"\n📅 Seasons ({len(seasons)}):")
        for season in seasons:
            count = (df['SEASON'] == season).sum()
            print(f"     {season}: {count:,} games")
    
    # Count teams
    all_teams = set(df['HOME_TEAM_ID']).union(set(df['AWAY_TEAM_ID']))
    
    if verbose:
        print(f"\n👥 Teams: {len(all_teams)}")
        print(f"\n🧮 Expected removal range:")
        print(f"   Minimum: {len(seasons) * 15} games (all mutual first games)")
        print(f"   Maximum: {len(seasons) * 30} games (no mutual first games)")
    
    # Process each season INDEPENDENTLY
    games_to_remove = []
    season_stats = []
    
    if verbose:
        print(f"\n🔄 Processing each season independently...")
    
    for season in seasons:
        # Get ONLY this season's games
        season_df = df[df['SEASON'] == season].copy()
        season_df = season_df.sort_values('GAME_DATE').reset_index(drop=False)
        
        # FRESH counters for THIS season only
        team_game_count = {}
        season_removed_indices = []
        
        for _, row in season_df.iterrows():
            original_idx = row['index']  # Original index in full df
            
            home = row['HOME_TEAM_ID']
            away = row['AWAY_TEAM_ID']
            
            # Initialize if first time seeing team THIS SEASON
            if home not in team_game_count:
                team_game_count[home] = 0
            if away not in team_game_count:
                team_game_count[away] = 0
            
            # Increment counters
            team_game_count[home] += 1
            team_game_count[away] += 1
            
            home_num = team_game_count[home]
            away_num = team_game_count[away]
            
            # Check if either team in first N games
            if home_num <= n_games or away_num <= n_games:
                season_removed_indices.append(original_idx)
        
        games_to_remove.extend(season_removed_indices)
        
        teams_in_season = len(team_game_count)
        removed_count = len(season_removed_indices)
        
        season_stats.append({
            'season': season,
            'teams': teams_in_season,
            'games': len(season_df),
            'removed': removed_count,
            'min_expected': 15,  # All mutual
            'max_expected': min(30, teams_in_season),  # No mutual
        })
        
        if verbose:
            print(f"\n   {season}:")
            print(f"     Teams: {teams_in_season}")
            print(f"     Total games: {len(season_df):,}")
            print(f"     Removed: {removed_count}")
            print(f"     Expected range: [{15}, {min(30, teams_in_season)}]")
            
            # Verify within bounds
            if removed_count < 15:
                print(f"     ⚠️  LESS than minimum (impossible!)")
            elif removed_count > min(30, teams_in_season):
                print(f"     ⚠️  MORE than maximum (BUG!)")
            else:
                print(f"     ✅ Within expected range")
    
    # Create removal mask
    remove_mask = pd.Series(False, index=df.index)
    remove_mask.loc[games_to_remove] = True
    
    total_removed = len(games_to_remove)
    
    # Verify total
    total_min = len(seasons) * 15
    total_max = len(seasons) * 30
    
    if verbose:
        print(f"\n" + "=" * 80)
        print("VERIFICATION")
        print("=" * 80)
        
        print(f"\n📊 Total removal:")
        print(f"   Removed: {total_removed}")
        print(f"   Expected range: [{total_min}, {total_max}]")
        
        if total_removed < total_min:
            print(f"   ❌ IMPOSSIBLE: Less than minimum!")
        elif total_removed > total_max:
            print(f"   ❌ BUG: More than maximum by {total_removed - total_max}!")
        else:
            print(f"   ✅ VALID: Within expected range")
    
    # Create cleaned dataframe
    df_cleaned = df[~remove_mask].copy()
    
    # Verify W = L
    if 'HOME_WIN' in df_cleaned.columns:
        home_wins = df_cleaned['HOME_WIN'].sum()
        away_wins = (1 - df_cleaned['HOME_WIN']).sum()
        w_equals_l = (home_wins == away_wins)
        
        if verbose:
            print(f"\n⚖️  Win/Loss Balance:")
            print(f"   Home wins: {home_wins:,}")
            print(f"   Away wins: {away_wins:,}")
            print(f"   Balanced: {'✅ Yes' if w_equals_l else f'❌ No (diff: {abs(home_wins - away_wins)})'}")
    else:
        home_wins = 0
        away_wins = 0
        w_equals_l = None
    
    # Check _PRIOR
    prior_cols = [col for col in df_cleaned.columns if '_PRIOR' in col]
    prior_missing = df_cleaned[prior_cols].isnull().sum().sum() if prior_cols else 0
    
    if verbose:
        print(f"\n🔍 Missing _PRIOR values:")
        print(f"   _PRIOR columns: {len(prior_cols)}")
        print(f"   Missing: {prior_missing:,}")
        print(f"   Clean: {'✅ Yes' if prior_missing == 0 else f'⚠️  No'}")
    
    # Save
    df_cleaned.to_csv(output_file, index=False)
    
    if verbose:
        file_size = os.path.getsize(output_file) / (1024**2)
        print(f"\n💾 Saved: {output_file}")
        print(f"   File size: {file_size:.2f} MB")
        
        print("\n" + "=" * 80)
        if total_removed <= total_max and prior_missing == 0 and w_equals_l:
            print("✅ SUCCESS: All checks passed!")
        else:
            print("⚠️  COMPLETE: Check warnings above")
        print("=" * 80)
    
    stats = {
        'original_games': original_size,
        'removed_games': total_removed,
        'final_games': len(df_cleaned),
        'removal_pct': (total_removed / original_size * 100),
        'home_wins': int(home_wins),
        'away_wins': int(away_wins),
        'w_equals_l': w_equals_l,
        'prior_missing': int(prior_missing),
        'within_bounds': (total_min <= total_removed <= total_max),
        'season_stats': season_stats
    }
    
    return df_cleaned, stats


def verify_old_vs_new(input_file, n_games=1):
    """
    Compare old logic vs new fixed logic.
    """
    print("\n" + "=" * 80)
    print("COMPARISON: OLD LOGIC vs FIXED LOGIC")
    print("=" * 80)
    
    df = pd.read_csv(input_file)
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    
    # OLD LOGIC (possibly buggy)
    print("\n🔴 OLD LOGIC:")
    df_sorted = df.sort_values(['SEASON', 'GAME_DATE']).reset_index(drop=True)
    
    remove_mask_old = pd.Series(False, index=df_sorted.index)
    
    for season in df_sorted['SEASON'].unique():
        season_idx = df_sorted.index[df_sorted['SEASON'] == season]
        season_df = df_sorted.loc[season_idx]
        
        team_game_count = {}
        
        for idx, row in season_df.iterrows():
            home = row['HOME_TEAM_ID']
            away = row['AWAY_TEAM_ID']
            
            if home not in team_game_count:
                team_game_count[home] = 0
            if away not in team_game_count:
                team_game_count[away] = 0
            
            team_game_count[home] += 1
            team_game_count[away] += 1
            
            if team_game_count[home] <= n_games or team_game_count[away] <= n_games:
                remove_mask_old.loc[idx] = True
    
    old_removed = remove_mask_old.sum()
    print(f"   Removed: {old_removed}")
    
    # NEW LOGIC (fixed)
    print("\n🟢 NEW FIXED LOGIC:")
    _, stats = remove_first_games_FIXED(input_file, "temp_test.csv", n_games=n_games, verbose=False)
    new_removed = stats['removed_games']
    print(f"   Removed: {new_removed}")
    
    # Comparison
    print(f"\n📊 COMPARISON:")
    print(f"   Old: {old_removed}")
    print(f"   New: {new_removed}")
    print(f"   Difference: {old_removed - new_removed:+d}")
    
    if old_removed == new_removed:
        print(f"   ⚠️  No difference - bug might be elsewhere")
    else:
        print(f"   ✅ Fixed! Reduced by {old_removed - new_removed} games")
    
    # Cleanup
    if os.path.exists("temp_test.csv"):
        os.remove("temp_test.csv")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "FIXED: REMOVE FIRST GAMES" + " " * 32 + "║")
    print("╚" + "═" * 78 + "╝")
    
    INPUT = "data/processed/nba/nba_game_level_with_rest.csv"
    OUTPUT = "data/processed/nba/nba_train_data.csv"
    N = 1
    
    print("\nOptions:")
    print("  1 - Compare old vs new logic")
    print("  2 - Run FIXED removal")
    print("  3 - Exit")
    
    choice = input("\nChoice: ").strip()
    
    try:
        if choice == "1":
            verify_old_vs_new(INPUT, n_games=N)
            
        elif choice == "2":
            df_cleaned, stats = remove_first_games_FIXED(INPUT, OUTPUT, n_games=N, verbose=True)
            
            if not stats['within_bounds']:
                print("\n⚠️  WARNING: Still removing more than maximum!")
                print("    This suggests a data issue, not a code bug")
                print("    Check if you have duplicate games or wrong data")
            
        else:
            print("\n❌ Exiting...")
            
    except FileNotFoundError:
        print(f"\n❌ File not found: {INPUT}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()