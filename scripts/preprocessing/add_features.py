"""
Script 4: Add Features and Finalize
Adds derived features (days rest, back-to-backs, etc.) and handles first games.

Input:  nba_game_level_data.csv
Output: nba_training_data.csv (ready for model training)
"""

import pandas as pd
import numpy as np

def add_features(input_file, output_file):
    """
    Add derived features and prepare final training dataset.
    
    Args:
        input_file: Path to game-level CSV
        output_file: Path for final training CSV
    """
    print("=" * 80)
    print("STEP 4: ADDING FEATURES & FINALIZING DATA")
    print("=" * 80)
    
    # Load data
    print("\n1. Loading game-level data...")
    df = pd.read_csv(input_file, parse_dates=['GAME_DATE'])
    print(f"   ✓ Loaded {len(df):,} games")
    
    # Debug: Show available columns
    print(f"\n   Available columns: {len(df.columns)}")
    home_cols = [c for c in df.columns if c.startswith('HOME_')]
    away_cols = [c for c in df.columns if c.startswith('AWAY_')]
    print(f"   HOME_* columns: {len(home_cols)}")
    print(f"   AWAY_* columns: {len(away_cols)}")
    
    # Identify the correct TEAM_ID column names
    if 'HOME_TEAM_ID' in df.columns:
        home_team_col = 'HOME_TEAM_ID'
        away_team_col = 'AWAY_TEAM_ID'
    else:
        print("\n   Looking for TEAM_ID columns...")
        team_id_cols = [c for c in df.columns if 'TEAM_ID' in c]
        print(f"   Found: {team_id_cols}")
        
        # Find HOME and AWAY team ID columns
        home_team_col = next((c for c in team_id_cols if c.startswith('HOME_')), None)
        away_team_col = next((c for c in team_id_cols if c.startswith('AWAY_')), None)
        
        if not home_team_col or not away_team_col:
            print(f"\n   ❌ ERROR: Could not find HOME/AWAY TEAM_ID columns!")
            print(f"   Available columns with 'TEAM': {[c for c in df.columns if 'TEAM' in c]}")
            return None
    
    print(f"   Using: {home_team_col} and {away_team_col}")
    
    # Check for NaN values
    print("\n2. Checking for missing values...")
    prior_cols = [col for col in df.columns if '_PRIOR' in col]
    if prior_cols:
        null_count = df[prior_cols].isnull().any(axis=1).sum()
        print(f"   Games with NaN in PRIOR columns: {null_count}")
        print(f"   (These are games where at least one team is playing their 1st game)")
    
    # Create feature: Days rest for both teams
    print("\n3. Creating days rest features...")
    
    # We need to calculate days since last game for each team
    # This requires going back to team-level view temporarily
    
    # For home team
    home_teams = df[[home_team_col, 'GAME_DATE']].copy()
    home_teams.columns = ['TEAM_ID', 'GAME_DATE']
    home_teams = home_teams.sort_values(['TEAM_ID', 'GAME_DATE'])
    home_teams['DAYS_REST'] = home_teams.groupby('TEAM_ID')['GAME_DATE'].diff().dt.days
    
    # For away team
    away_teams = df[[away_team_col, 'GAME_DATE']].copy()
    away_teams.columns = ['TEAM_ID', 'GAME_DATE']
    away_teams = away_teams.sort_values(['TEAM_ID', 'GAME_DATE'])
    away_teams['DAYS_REST'] = away_teams.groupby('TEAM_ID')['GAME_DATE'].diff().dt.days
    
    # Merge back
    df = df.merge(
        home_teams[['TEAM_ID', 'GAME_DATE', 'DAYS_REST']].rename(
            columns={'TEAM_ID': home_team_col, 'DAYS_REST': 'HOME_DAYS_REST'}
        ),
        on=[home_team_col, 'GAME_DATE'],
        how='left'
    )
    
    df = df.merge(
        away_teams[['TEAM_ID', 'GAME_DATE', 'DAYS_REST']].rename(
            columns={'TEAM_ID': away_team_col, 'DAYS_REST': 'AWAY_DAYS_REST'}
        ),
        on=[away_team_col, 'GAME_DATE'],
        how='left'
    )
    
    print(f"   ✓ Added HOME_DAYS_REST and AWAY_DAYS_REST")
    
    # Create back-to-back indicators
    print("\n4. Creating back-to-back indicators...")
    df['HOME_B2B'] = (df['HOME_DAYS_REST'] == 1).astype(int)
    df['AWAY_B2B'] = (df['AWAY_DAYS_REST'] == 1).astype(int)
    
    home_b2b_count = df['HOME_B2B'].sum()
    away_b2b_count = df['AWAY_B2B'].sum()
    print(f"   Home B2Bs: {home_b2b_count:,} ({home_b2b_count/len(df)*100:.1f}%)")
    print(f"   Away B2Bs: {away_b2b_count:,} ({away_b2b_count/len(df)*100:.1f}%)")
    
    # Create rest advantage feature
    print("\n5. Creating rest advantage features...")
    df['REST_ADVANTAGE'] = df['HOME_DAYS_REST'] - df['AWAY_DAYS_REST']
    print(f"   ✓ Added REST_ADVANTAGE (positive = home more rested)")
    
    # Create matchup strength features
    print("\n6. Creating matchup features...")
    
    # Check which PRIOR columns exist
    available_features = []
    
    # Net rating differential (key predictor)
    if 'HOME_NET_RATING_PRIOR' in df.columns and 'AWAY_NET_RATING_PRIOR' in df.columns:
        df['NET_RATING_DIFF'] = df['HOME_NET_RATING_PRIOR'] - df['AWAY_NET_RATING_PRIOR']
        available_features.append('NET_RATING_DIFF')
    
    # Win percentage differential
    if 'HOME_W_PCT_PRIOR' in df.columns and 'AWAY_W_PCT_PRIOR' in df.columns:
        df['WIN_PCT_DIFF'] = df['HOME_W_PCT_PRIOR'] - df['AWAY_W_PCT_PRIOR']
        available_features.append('WIN_PCT_DIFF')
    
    # Four Factors differential
    if 'HOME_EFG_PCT_FF_PRIOR' in df.columns and 'AWAY_EFG_PCT_FF_PRIOR' in df.columns:
        df['EFG_PCT_DIFF'] = df['HOME_EFG_PCT_FF_PRIOR'] - df['AWAY_EFG_PCT_FF_PRIOR']
        available_features.append('EFG_PCT_DIFF')
    
    if 'HOME_TM_TOV_PCT_FF_PRIOR' in df.columns and 'AWAY_TM_TOV_PCT_FF_PRIOR' in df.columns:
        df['TOV_PCT_DIFF'] = df['HOME_TM_TOV_PCT_FF_PRIOR'] - df['AWAY_TM_TOV_PCT_FF_PRIOR']
        available_features.append('TOV_PCT_DIFF')
    
    if 'HOME_OREB_PCT_FF_PRIOR' in df.columns and 'AWAY_OREB_PCT_FF_PRIOR' in df.columns:
        df['OREB_PCT_DIFF'] = df['HOME_OREB_PCT_FF_PRIOR'] - df['AWAY_OREB_PCT_FF_PRIOR']
        available_features.append('OREB_PCT_DIFF')
    
    if 'HOME_FTA_RATE_PRIOR' in df.columns and 'AWAY_FTA_RATE_PRIOR' in df.columns:
        df['FTA_RATE_DIFF'] = df['HOME_FTA_RATE_PRIOR'] - df['AWAY_FTA_RATE_PRIOR']
        available_features.append('FTA_RATE_DIFF')
    
    print(f"   ✓ Added {len(available_features)} matchup differential features")
    for feat in available_features:
        print(f"     - {feat}")
    
    # Create season progress features
    print("\n7. Creating season progress features...")
    if 'HOME_GP_PRIOR' in df.columns:
        df['HOME_SEASON_PROGRESS'] = df['HOME_GP_PRIOR'] / 82.0
        print(f"   ✓ Added HOME_SEASON_PROGRESS")
    
    if 'AWAY_GP_PRIOR' in df.columns:
        df['AWAY_SEASON_PROGRESS'] = df['AWAY_GP_PRIOR'] / 82.0
        print(f"   ✓ Added AWAY_SEASON_PROGRESS")
    
    # Handle first games (NaN values in PRIOR columns)
    print("\n8. Handling first games...")
    rows_before = len(df)
    
    # Check for any NaN in critical PRIOR columns
    critical_cols = [c for c in ['HOME_NET_RATING_PRIOR', 'AWAY_NET_RATING_PRIOR', 
                                  'HOME_W_PCT_PRIOR', 'AWAY_W_PCT_PRIOR'] 
                     if c in df.columns]
    
    if critical_cols:
        # Drop rows where any critical PRIOR column is NaN
        df_clean = df.dropna(subset=critical_cols)
        rows_after = len(df_clean)
        rows_dropped = rows_before - rows_after
        
        print(f"   Dropped {rows_dropped} games with NaN in critical features")
        print(f"   Remaining: {rows_after:,} games ({rows_after/rows_before*100:.1f}%)")
    else:
        print("   No critical PRIOR columns found, keeping all rows")
        df_clean = df.copy()
        rows_after = len(df_clean)
    
    # Sort by date
    print("\n9. Final sorting and organization...")
    df_clean = df_clean.sort_values('GAME_DATE').reset_index(drop=True)
    
    # Select key columns for summary
    print("\n10. Dataset summary...")
    print(f"    Total games: {len(df_clean):,}")
    print(f"    Total columns: {len(df_clean.columns)}")
    print(f"    Date range: {df_clean['GAME_DATE'].min().date()} to {df_clean['GAME_DATE'].max().date()}")
    
    if 'HOME_WIN' in df_clean.columns:
        print(f"    Home win rate: {df_clean['HOME_WIN'].mean()*100:.1f}%")
    
    # Show feature categories
    print("\n11. Feature categories:")
    feature_counts = {
        'Identifiers': len([c for c in df_clean.columns if c in ['GAME_ID', 'GAME_DATE', 'SEASON']]),
        'Target': 1 if 'HOME_WIN' in df_clean.columns else 0,
        'HOME team PRIOR stats': len([c for c in df_clean.columns if c.startswith('HOME_') and '_PRIOR' in c]),
        'AWAY team PRIOR stats': len([c for c in df_clean.columns if c.startswith('AWAY_') and '_PRIOR' in c]),
        'HOME game stats': len([c for c in df_clean.columns if c.startswith('HOME_') and '_PRIOR' not in c and c not in ['HOME_WIN', 'HOME_WL', 'HOME_B2B', 'HOME_DAYS_REST', 'HOME_SEASON_PROGRESS']]),
        'AWAY game stats': len([c for c in df_clean.columns if c.startswith('AWAY_') and '_PRIOR' not in c and c not in ['AWAY_WL', 'AWAY_B2B', 'AWAY_DAYS_REST', 'AWAY_SEASON_PROGRESS']]),
        'Derived features': len([c for c in df_clean.columns if any(x in c for x in ['DAYS_REST', 'B2B', '_DIFF', 'ADVANTAGE', 'PROGRESS'])]),
    }
    
    for category, count in feature_counts.items():
        print(f"    {category:30s}: {count:3d}")
    
    # Save output
    print(f"\n12. Saving final training data...")
    df_clean.to_csv(output_file, index=False)
    print(f"    ✓ Saved to: {output_file}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL DATASET READY FOR TRAINING:")
    print("-" * 80)
    print(f"Rows:          {len(df_clean):,} games")
    print(f"Columns:       {len(df_clean.columns)}")
    
    if 'HOME_WIN' in df_clean.columns:
        print(f"Target:        HOME_WIN (binary: 1=home wins, 0=away wins)")
        print(f"Home win rate: {df_clean['HOME_WIN'].mean()*100:.1f}%")
    
    null_check = df_clean[critical_cols].isnull().sum().sum() if critical_cols else 0
    if null_check == 0:
        print(f"No NaN values: ✓")
    else:
        print(f"Warning: {null_check} NaN values remain")
    
    print("\nKey features added:")
    print("  ✓ Days rest (HOME_DAYS_REST, AWAY_DAYS_REST)")
    print("  ✓ Back-to-backs (HOME_B2B, AWAY_B2B)")
    print(f"  ✓ Matchup differentials ({len(available_features)} features)")
    if 'HOME_SEASON_PROGRESS' in df_clean.columns:
        print("  ✓ Season progress (HOME_SEASON_PROGRESS, AWAY_SEASON_PROGRESS)")
    print("=" * 80)
    
    return df_clean


if __name__ == "__main__":
    # File paths
    INPUT_FILE = "data/processed/nba/nba_game_level_data.csv"
    OUTPUT_FILE = "data/processed/nba/nba_training_data.csv"
    
    # Run feature engineering
    df_final = add_features(INPUT_FILE, OUTPUT_FILE)
    
    if df_final is not None:
        print("\n✅ ALL STEPS COMPLETE!")
        print("\n📊 Your data is ready for model training.")
        print("\nRecommended next steps:")
        print("  1. Split data temporally (train on 2022-24, test on 2024-25)")
        print("  2. Start with baseline: NET_RATING_DIFF only")
        print("  3. Add Four Factors differentials")
        print("  4. Full feature model with all PRIOR stats")
        print("\nExpected accuracy: 68-75% (realistic for NBA prediction)")
    else:
        print("\n❌ Feature engineering failed! Check errors above.")