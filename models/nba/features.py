"""
Minimal Feature Engineering (REST & B2B Only)
==============================================

This version adds ONLY schedule-based features (no rolling averages).
Use this BEFORE removing first games.

Features added:
1. REST_DAYS (schedule-based, known pre-game)
2. B2B indicators (derived from REST)
3. REST_ADVANTAGE (differential)

Run rolling averages AFTER removing first games in a separate script.

Author: Oleksandr
Date: November 25, 2024
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def calculate_rest_days(df, verbose=True):
    """
    Calculate days rest for each team (home and away).
    
    ⚠️ DATA LEAKAGE CHECK: ✅ SAFE
    - REST is KNOWN BEFORE the game starts (pre-game knowledge)
    - We calculate: days between CURRENT game and PREVIOUS game
    - This is public information available before tipoff
    """
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 1: CALCULATING REST DAYS (No Leakage)")
        print("=" * 80)
        print("   ℹ️  REST is pre-game knowledge (schedule-based)")
    
    df = df.copy()
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values(['SEASON', 'GAME_DATE']).reset_index(drop=True)
    
    # Initialize columns
    df['HOME_DAYS_REST'] = np.nan
    df['AWAY_DAYS_REST'] = np.nan
    
    # Process each season separately
    seasons = df['SEASON'].unique()
    
    for season in seasons:
        season_mask = df['SEASON'] == season
        season_df = df[season_mask].copy()
        
        # Track last game date for each team
        team_last_game = {}
        
        for idx in season_df.index:
            row = df.loc[idx]
            home_team = row['HOME_TEAM_ID']
            away_team = row['AWAY_TEAM_ID']
            game_date = row['GAME_DATE']
            
            # Calculate home team rest
            if home_team in team_last_game:
                days_rest = (game_date - team_last_game[home_team]).days
                df.loc[idx, 'HOME_DAYS_REST'] = days_rest
            
            # Calculate away team rest
            if away_team in team_last_game:
                days_rest = (game_date - team_last_game[away_team]).days
                df.loc[idx, 'AWAY_DAYS_REST'] = days_rest
            
            # Update last game dates AFTER calculating rest
            team_last_game[home_team] = game_date
            team_last_game[away_team] = game_date
    
    if verbose:
        print(f"\n✓ Calculated rest days (pre-game knowledge)")
        print(f"  HOME_DAYS_REST range: {df['HOME_DAYS_REST'].min():.0f} to {df['HOME_DAYS_REST'].max():.0f} days")
        print(f"  AWAY_DAYS_REST range: {df['AWAY_DAYS_REST'].min():.0f} to {df['AWAY_DAYS_REST'].max():.0f} days")
        print(f"  Missing values (first games): {df['HOME_DAYS_REST'].isnull().sum()}")
        print(f"  ✅ No data leakage - REST known before tipoff!")
    
    return df


def calculate_b2b_and_rest_advantage(df, verbose=True):
    """
    Calculate back-to-back indicators and rest advantage.
    
    ⚠️ DATA LEAKAGE CHECK: ✅ SAFE
    - B2B is KNOWN BEFORE the game (based on REST, which is schedule-based)
    - REST_ADVANTAGE is KNOWN BEFORE the game (pre-game knowledge)
    """
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 2: CALCULATING B2B AND REST ADVANTAGE (No Leakage)")
        print("=" * 80)
        print("   ℹ️  B2B and REST_ADVANTAGE are pre-game knowledge")
    
    df = df.copy()
    
    # Back-to-back indicators (1 day or less rest)
    df['HOME_B2B'] = (df['HOME_DAYS_REST'] <= 1).astype(int)
    df['AWAY_B2B'] = (df['AWAY_DAYS_REST'] <= 1).astype(int)
    
    # Rest advantage (positive = home team more rested)
    df['REST_ADVANTAGE'] = df['HOME_DAYS_REST'] - df['AWAY_DAYS_REST']
    
    if verbose:
        home_b2b_pct = df['HOME_B2B'].mean() * 100
        away_b2b_pct = df['AWAY_B2B'].mean() * 100
        
        print(f"\n✓ Back-to-back games (pre-game knowledge):")
        print(f"  HOME_B2B: {df['HOME_B2B'].sum()} games ({home_b2b_pct:.1f}%)")
        print(f"  AWAY_B2B: {df['AWAY_B2B'].sum()} games ({away_b2b_pct:.1f}%)")
        
        print(f"\n✓ Rest advantage (pre-game knowledge):")
        print(f"  Mean: {df['REST_ADVANTAGE'].mean():.2f} days")
        print(f"  Std: {df['REST_ADVANTAGE'].std():.2f} days")
        print(f"  Range: [{df['REST_ADVANTAGE'].min():.0f}, {df['REST_ADVANTAGE'].max():.0f}]")
        print(f"  ✅ No data leakage - all schedule-based!")
    
    return df


def minimal_feature_engineering(input_file, output_file, verbose=True):
    """
    Minimal feature engineering - REST and B2B only.
    
    Run this BEFORE removing first games.
    Add rolling averages AFTER removing first games.
    """
    
    if verbose:
        print("\n")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 15 + "MINIMAL FEATURE ENGINEERING (REST/B2B)" + " " * 22 + "║")
        print("╚" + "═" * 78 + "╝")
        print(f"\nInput:  {input_file}")
        print(f"Output: {output_file}")
        print("\n⚠️  This adds ONLY REST/B2B features (no rolling averages)")
        print("   Run rolling averages AFTER removing first games!")
    
    # Load data
    if verbose:
        print("\n" + "=" * 80)
        print("LOADING DATA")
        print("=" * 80)
    
    df = pd.read_csv(input_file)
    original_cols = len(df.columns)
    original_rows = len(df)
    
    if verbose:
        print(f"\n✓ Loaded {original_rows:,} games")
        print(f"  Original columns: {original_cols}")
        print(f"  Date range: {df['GAME_DATE'].min()} to {df['GAME_DATE'].max()}")
    
    # Run minimal pipeline
    df = calculate_rest_days(df, verbose=verbose)
    df = calculate_b2b_and_rest_advantage(df, verbose=verbose)
    
    # Save
    if verbose:
        print("\n" + "=" * 80)
        print("SAVING MINIMAL FEATURES")
        print("=" * 80)
    
    df.to_csv(output_file, index=False)
    
    final_cols = len(df.columns)
    new_cols = final_cols - original_cols
    
    if verbose:
        import os
        file_size = os.path.getsize(output_file) / (1024**2)
        
        print(f"\n✓ Saved to: {output_file}")
        print(f"  File size: {file_size:.2f} MB")
        print(f"  Final columns: {final_cols} (+{new_cols} new features)")
        print(f"  Rows: {len(df):,} (unchanged)")
    
    # Summary
    if verbose:
        print("\n" + "=" * 80)
        print("SUMMARY: FEATURES ADDED")
        print("=" * 80)
        
        new_features = [col for col in df.columns if col not in pd.read_csv(input_file).columns]
        
        print(f"\n📊 Total new features: {len(new_features)}")
        print(f"\n✅ REST & Schedule Features:")
        for f in new_features:
            print(f"   - {f}")
        
        print("\n" + "=" * 80)
        print("✅ MINIMAL FEATURES COMPLETE!")
        print("=" * 80)
        
        print("\n🎯 Next steps:")
        print("   1. Remove first games (eliminates NaN in REST and _PRIOR)")
        print("   2. Add rolling averages (will have no NaN)")
        print("   3. Add form indicators (will have no NaN)")
        print("   4. Train model")
        
        print("\n📈 Expected impact from REST/B2B alone:")
        print("   Current accuracy: 61.5%")
        print("   With REST_ADVANTAGE: 63-65% (+2-3%)")
        print("   (Rolling averages will add another +3-5%)")
    
    return df


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MINIMAL FEATURE ENGINEERING (REST/B2B ONLY)")
    print("=" * 80)
    
    INPUT_FILE = "data/processed/nba/nba_game_level_data.csv"
    OUTPUT_FILE = "data/processed/nba/nba_game_level_with_rest.csv"
    
    print(f"\n📁 Configuration:")
    print(f"   Input:  {INPUT_FILE}")
    print(f"   Output: {OUTPUT_FILE}")
    
    print("\n💡 Strategy:")
    print("   1. Add REST/B2B now (simple, schedule-based)")
    print("   2. Remove first games (cleans _PRIOR NaN)")
    print("   3. Add rolling averages later (no NaN issues)")
    
    response = input("\nProceed? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            df = minimal_feature_engineering(
                INPUT_FILE,
                OUTPUT_FILE,
                verbose=True
            )
            
            print("\n🎉 SUCCESS!")
            print(f"   File saved: {OUTPUT_FILE}")
            print(f"\n   Next: python remove_first_games_FIXED.py")
            
        except FileNotFoundError:
            print(f"\n❌ File not found: {INPUT_FILE}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ Cancelled")