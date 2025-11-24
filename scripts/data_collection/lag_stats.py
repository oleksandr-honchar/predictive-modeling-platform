"""
Script 1: Lag Stats File
Creates lagged (_PRIOR) versions of all cumulative/season-to-date statistics.
This prevents data leakage by showing team stats BEFORE each game.

Input:  nba_stats_all_data_cleaned.csv
Output: nba_stats_lagged.csv
"""

import pandas as pd
import numpy as np

def lag_stats(input_file, output_file):
    """
    Create lagged versions of cumulative stats to prevent data leakage.
    
    Args:
        input_file: Path to stats CSV
        output_file: Path for output CSV with lagged columns
    """
    print("=" * 80)
    print("STEP 1: CREATING LAGGED FEATURES")
    print("=" * 80)
    
    # Load data
    print("\n1. Loading data...")
    df = pd.read_csv(input_file)
    print(f"   ✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    # Sort by team and date (critical for proper lagging)
    print("\n2. Sorting by TEAM_ID and GAME_DATE...")
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values(['TEAM_ID', 'GAME_DATE']).reset_index(drop=True)
    print("   ✓ Data sorted chronologically by team")
    
    # Define columns to lag (all cumulative/season-to-date stats)
    columns_to_lag = [
        # Cumulative stats
        'GP', 'W', 'L', 'W_PCT', 'MIN',
        
        # Advanced ratings (season-to-date calculations)
        'OFF_RATING', 'DEF_RATING', 'NET_RATING',
        'E_OFF_RATING', 'E_DEF_RATING', 'E_NET_RATING',
        
        # Team metrics
        'AST_PCT', 'AST_TO', 'AST_RATIO',
        'DREB_PCT', 'REB_PCT', 'TS_PCT',
        
        # Pace and possessions
        'E_PACE', 'PACE', 'PACE_PER40', 'POSS', 'PIE',
        
        # Four Factors - Team
        'EFG_PCT_FF', 'FTA_RATE', 'TM_TOV_PCT_FF', 'OREB_PCT_FF',
        
        # Four Factors - Opponent
        'OPP_EFG_PCT', 'OPP_FTA_RATE', 'OPP_TOV_PCT', 'OPP_OREB_PCT'
    ]
    
    # Filter to only columns that exist in the dataframe
    columns_to_lag = [col for col in columns_to_lag if col in df.columns]
    
    print(f"\n3. Creating lagged features for {len(columns_to_lag)} columns...")
    
    # Create lagged versions
    for col in columns_to_lag:
        lagged_col = f'{col}_PRIOR'
        # Shift by 1 within each team (previous game's value)
        df[lagged_col] = df.groupby('TEAM_ID')[col].shift(1)
    
    print(f"   ✓ Created {len(columns_to_lag)} _PRIOR columns")
    
    # Verify lagging
    print("\n4. Verifying lagged features...")
    sample_team = df['TEAM_ID'].iloc[0]
    sample = df[df['TEAM_ID'] == sample_team].head(3)
    
    print(f"\n   Sample: First 3 games for TEAM_ID {sample_team}")
    print("   " + "-" * 76)
    display_cols = ['GAME_DATE', 'W', 'W_PRIOR', 'L', 'L_PRIOR', 
                    'NET_RATING', 'NET_RATING_PRIOR']
    
    for idx, row in sample[display_cols].iterrows():
        # Format each value separately before using in f-string
        date_str = row['GAME_DATE'].strftime('%Y-%m-%d')
        w_val = f"{row['W']:.0f}"
        w_prior_val = f"{row['W_PRIOR']:.0f}" if pd.notna(row['W_PRIOR']) else 'NaN'
        l_val = f"{row['L']:.0f}"
        l_prior_val = f"{row['L_PRIOR']:.0f}" if pd.notna(row['L_PRIOR']) else 'NaN'
        net_val = f"{row['NET_RATING']:.1f}"
        net_prior_val = f"{row['NET_RATING_PRIOR']:.1f}" if pd.notna(row['NET_RATING_PRIOR']) else 'NaN'
        
        print(f"   {date_str}: "
              f"W={w_val:>3s} W_PRIOR={w_prior_val:>3s} | "
              f"L={l_val:>3s} L_PRIOR={l_prior_val:>3s} | "
              f"NET={net_val:>5s} NET_PRIOR={net_prior_val:>5s}")
    
    # Check NaN counts
    print("\n5. Checking for NaN values...")
    null_counts = df[[f'{col}_PRIOR' for col in columns_to_lag]].isnull().sum()
    print(f"   NaN per lagged column: Min={null_counts.min()}, "
          f"Max={null_counts.max()}, Mean={null_counts.mean():.1f}")
    print(f"   (Expected: ~30 NaN per column = first game for each team)")
    
    # Save output
    print(f"\n6. Saving lagged data...")
    df.to_csv(output_file, index=False)
    print(f"   ✓ Saved to: {output_file}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("-" * 80)
    print(f"Input columns:  {len(df.columns) - len(columns_to_lag)}")
    print(f"Lagged columns: {len(columns_to_lag)}")
    print(f"Total columns:  {len(df.columns)}")
    print(f"Total rows:     {len(df):,}")
    print(f"First games with NaN: ~{df.groupby('TEAM_ID').size().shape[0]} (one per team)")
    print("=" * 80)
    
    return df


if __name__ == "__main__":
    # File paths
    INPUT_FILE = "data/raw/nba/nba_stats_all_data_cleaned.csv"
    OUTPUT_FILE = "data/processed/nba/nba_stats_lagged.csv"
    
    # Run the lagging
    df_lagged = lag_stats(INPUT_FILE, OUTPUT_FILE)
    
    print("\n✅ STEP 1 COMPLETE: Stats file lagged successfully!")
    print(f"Next: Run script 02_merge_team_data.py")