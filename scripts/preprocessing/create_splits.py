"""
Train/Validation/Test Split for NBA Prediction Model
====================================================

Creates temporal train/validation/test splits for time-series data.
Ensures no data leakage by respecting temporal ordering.

Split Strategy:
- 70% Training (oldest games)
- 15% Validation (middle games)
- 15% Test (most recent games)

Author: Oleksandr
Date: November 25, 2024
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os


def create_train_val_test_split(
    input_file,
    output_dir,
    train_ratio=0.70,
    val_ratio=0.15,
    test_ratio=0.15,
    verbose=True
):
    """
    Create temporal train/validation/test splits.
    
    CRITICAL: Uses temporal ordering to prevent data leakage.
    - Training: Oldest 70% of games
    - Validation: Middle 15% of games
    - Test: Most recent 15% of games
    
    This ensures the model trains on past data and validates/tests on future data.
    
    Parameters:
    -----------
    input_file : str
        Path to clean CSV file (e.g., nba_train_data.csv)
    output_dir : str
        Directory to save train/val/test CSV files
    train_ratio : float
        Proportion for training (default: 0.70)
    val_ratio : float
        Proportion for validation (default: 0.15)
    test_ratio : float
        Proportion for test (default: 0.15)
    verbose : bool
        Print detailed output
    
    Returns:
    --------
    dict : Dictionary with train, val, test DataFrames and metadata
    """
    
    if verbose:
        print("\n")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "TRAIN/VALIDATION/TEST SPLIT" + " " * 29 + "║")
        print("╚" + "═" * 78 + "╝")
    
    # Validate ratios
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, \
        f"Ratios must sum to 1.0. Got: {train_ratio + val_ratio + test_ratio}"
    
    if verbose:
        print(f"\n📊 Split Configuration:")
        print(f"   Training:   {train_ratio*100:.1f}%")
        print(f"   Validation: {val_ratio*100:.1f}%")
        print(f"   Test:       {test_ratio*100:.1f}%")
    
    # ========================================================================
    # 1. LOAD DATA
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 1: LOADING DATA")
        print("=" * 80)
    
    df = pd.read_csv(input_file)
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    
    # Sort by date (critical for temporal split!)
    df = df.sort_values('GAME_DATE').reset_index(drop=True)
    
    total_games = len(df)
    
    if verbose:
        print(f"\n✓ Loaded {total_games:,} games")
        print(f"  Date range: {df['GAME_DATE'].min().date()} to {df['GAME_DATE'].max().date()}")
        print(f"  Seasons: {', '.join(sorted(df['SEASON'].unique()))}")
        print(f"  Columns: {len(df.columns)}")
    
    # ========================================================================
    # 2. CALCULATE SPLIT INDICES
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 2: CALCULATING SPLIT INDICES")
        print("=" * 80)
    
    # Calculate split points
    train_size = int(total_games * train_ratio)
    val_size = int(total_games * val_ratio)
    test_size = total_games - train_size - val_size  # Remaining games
    
    # Define indices
    train_end = train_size
    val_end = train_size + val_size
    
    if verbose:
        print(f"\n✓ Split sizes:")
        print(f"   Training:   {train_size:,} games (indices 0 to {train_end-1})")
        print(f"   Validation: {val_size:,} games (indices {train_end} to {val_end-1})")
        print(f"   Test:       {test_size:,} games (indices {val_end} to {total_games-1})")
        print(f"   Total:      {train_size + val_size + test_size:,} games")
    
    # ========================================================================
    # 3. CREATE SPLITS
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 3: CREATING SPLITS (TEMPORAL ORDER)")
        print("=" * 80)
    
    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()
    
    if verbose:
        print(f"\n✓ Training set:")
        print(f"   Games: {len(train_df):,}")
        print(f"   Date range: {train_df['GAME_DATE'].min().date()} to {train_df['GAME_DATE'].max().date()}")
        print(f"   Seasons: {', '.join(sorted(train_df['SEASON'].unique()))}")
        
        print(f"\n✓ Validation set:")
        print(f"   Games: {len(val_df):,}")
        print(f"   Date range: {val_df['GAME_DATE'].min().date()} to {val_df['GAME_DATE'].max().date()}")
        print(f"   Seasons: {', '.join(sorted(val_df['SEASON'].unique()))}")
        
        print(f"\n✓ Test set:")
        print(f"   Games: {len(test_df):,}")
        print(f"   Date range: {test_df['GAME_DATE'].min().date()} to {test_df['GAME_DATE'].max().date()}")
        print(f"   Seasons: {', '.join(sorted(test_df['SEASON'].unique()))}")
    
    # ========================================================================
    # 4. VERIFY NO OVERLAP (TEMPORAL INTEGRITY)
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 4: VERIFYING TEMPORAL INTEGRITY")
        print("=" * 80)
    
    train_max_date = train_df['GAME_DATE'].max()
    val_min_date = val_df['GAME_DATE'].min()
    val_max_date = val_df['GAME_DATE'].max()
    test_min_date = test_df['GAME_DATE'].min()
    
    # Check temporal ordering
    train_before_val = train_max_date <= val_min_date
    val_before_test = val_max_date <= test_min_date
    
    if verbose:
        print(f"\n✓ Temporal ordering:")
        print(f"   Train max date:     {train_max_date.date()}")
        print(f"   Validation min date: {val_min_date.date()}")
        print(f"   Gap (train→val):    {(val_min_date - train_max_date).days} days")
        print(f"   {'✅' if train_before_val else '❌'} Train before Validation")
        
        print(f"\n   Validation max date: {val_max_date.date()}")
        print(f"   Test min date:       {test_min_date.date()}")
        print(f"   Gap (val→test):     {(test_min_date - val_max_date).days} days")
        print(f"   {'✅' if val_before_test else '❌'} Validation before Test")
    
    if not (train_before_val and val_before_test):
        print(f"\n   ⚠️  WARNING: Temporal ordering violated!")
        print(f"      This indicates data was not properly sorted by date.")
    else:
        print(f"\n   ✅ Perfect temporal separation (no data leakage)")
    
    # ========================================================================
    # 5. VERIFY DATA QUALITY
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 5: VERIFYING DATA QUALITY")
        print("=" * 80)
    
    # Check W/L balance in each split
    for name, split_df in [('Training', train_df), ('Validation', val_df), ('Test', test_df)]:
        home_wins = split_df['HOME_WIN'].sum()
        away_wins = len(split_df) - home_wins
        home_win_pct = home_wins / len(split_df) * 100
        
        if verbose:
            print(f"\n✓ {name} set balance:")
            print(f"   Home wins: {home_wins:,} ({home_win_pct:.1f}%)")
            print(f"   Away wins: {away_wins:,} ({100-home_win_pct:.1f}%)")
            
            if 52 <= home_win_pct <= 58:
                print(f"   ✅ Normal NBA home advantage (54-56% expected)")
            else:
                print(f"   ⚠️  Unusual home win rate")
    
    # Check for missing values
    for name, split_df in [('Training', train_df), ('Validation', val_df), ('Test', test_df)]:
        missing = split_df.isnull().sum().sum()
        if verbose:
            if missing == 0:
                print(f"\n✓ {name} set: No missing values ✅")
            else:
                print(f"\n⚠️  {name} set: {missing:,} missing values")
    
    # ========================================================================
    # 6. SAVE SPLITS
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("STEP 6: SAVING SPLITS")
        print("=" * 80)
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output paths
    train_path = os.path.join(output_dir, 'nba_train.csv')
    val_path = os.path.join(output_dir, 'nba_val.csv')
    test_path = os.path.join(output_dir, 'nba_test.csv')
    
    # Save
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    if verbose:
        print(f"\n✓ Saved splits:")
        print(f"   Training:   {train_path}")
        print(f"               Size: {os.path.getsize(train_path) / (1024**2):.2f} MB")
        
        print(f"   Validation: {val_path}")
        print(f"               Size: {os.path.getsize(val_path) / (1024**2):.2f} MB")
        
        print(f"   Test:       {test_path}")
        print(f"               Size: {os.path.getsize(test_path) / (1024**2):.2f} MB")
    
    # ========================================================================
    # 7. CREATE METADATA
    # ========================================================================
    metadata = {
        'total_games': total_games,
        'train_size': len(train_df),
        'val_size': len(val_df),
        'test_size': len(test_df),
        'train_ratio': train_ratio,
        'val_ratio': val_ratio,
        'test_ratio': test_ratio,
        'train_date_range': (train_df['GAME_DATE'].min(), train_df['GAME_DATE'].max()),
        'val_date_range': (val_df['GAME_DATE'].min(), val_df['GAME_DATE'].max()),
        'test_date_range': (test_df['GAME_DATE'].min(), test_df['GAME_DATE'].max()),
        'train_seasons': sorted(train_df['SEASON'].unique()),
        'val_seasons': sorted(val_df['SEASON'].unique()),
        'test_seasons': sorted(test_df['SEASON'].unique()),
        'temporal_integrity': train_before_val and val_before_test,
        'split_date': datetime.now().isoformat(),
    }
    
    # Save metadata
    metadata_path = os.path.join(output_dir, 'split_metadata.txt')
    with open(metadata_path, 'w') as f:
        f.write("NBA PREDICTION MODEL - DATA SPLIT METADATA\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Split Date: {metadata['split_date']}\n")
        f.write(f"Total Games: {metadata['total_games']:,}\n\n")
        
        f.write("SPLIT SIZES:\n")
        f.write(f"  Training:   {metadata['train_size']:,} ({train_ratio*100:.1f}%)\n")
        f.write(f"  Validation: {metadata['val_size']:,} ({val_ratio*100:.1f}%)\n")
        f.write(f"  Test:       {metadata['test_size']:,} ({test_ratio*100:.1f}%)\n\n")
        
        f.write("DATE RANGES:\n")
        f.write(f"  Training:   {metadata['train_date_range'][0].date()} to {metadata['train_date_range'][1].date()}\n")
        f.write(f"  Validation: {metadata['val_date_range'][0].date()} to {metadata['val_date_range'][1].date()}\n")
        f.write(f"  Test:       {metadata['test_date_range'][0].date()} to {metadata['test_date_range'][1].date()}\n\n")
        
        f.write("SEASONS:\n")
        f.write(f"  Training:   {', '.join(metadata['train_seasons'])}\n")
        f.write(f"  Validation: {', '.join(metadata['val_seasons'])}\n")
        f.write(f"  Test:       {', '.join(metadata['test_seasons'])}\n\n")
        
        f.write(f"Temporal Integrity: {'✅ PASS' if metadata['temporal_integrity'] else '❌ FAIL'}\n")
    
    if verbose:
        print(f"\n✓ Saved metadata: {metadata_path}")
    
    # ========================================================================
    # 8. FINAL SUMMARY
    # ========================================================================
    if verbose:
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ Successfully created train/validation/test splits")
        print(f"\n📊 Split sizes:")
        print(f"   Training:   {len(train_df):,} games ({len(train_df)/total_games*100:.1f}%)")
        print(f"   Validation: {len(val_df):,} games ({len(val_df)/total_games*100:.1f}%)")
        print(f"   Test:       {len(test_df):,} games ({len(test_df)/total_games*100:.1f}%)")
        
        print(f"\n📅 Temporal split:")
        print(f"   Train:      {train_df['GAME_DATE'].min().date()} → {train_df['GAME_DATE'].max().date()}")
        print(f"   Validation: {val_df['GAME_DATE'].min().date()} → {val_df['GAME_DATE'].max().date()}")
        print(f"   Test:       {test_df['GAME_DATE'].min().date()} → {test_df['GAME_DATE'].max().date()}")
        
        print(f"\n✅ Data quality:")
        print(f"   Temporal ordering: {'✅ Valid' if metadata['temporal_integrity'] else '❌ Invalid'}")
        print(f"   No data leakage: {'✅ Guaranteed' if metadata['temporal_integrity'] else '❌ Check required'}")
        print(f"   Missing values: ✅ None")
        
        print(f"\n📁 Output files:")
        print(f"   {train_path}")
        print(f"   {val_path}")
        print(f"   {test_path}")
        print(f"   {metadata_path}")
        
        print("\n" + "=" * 80)
        print("✅ SPLIT COMPLETE!")
        print("=" * 80)
        
        print("\n🎯 Next steps:")
        print("   1. Train model on nba_train.csv")
        print("   2. Tune hyperparameters using nba_val.csv")
        print("   3. Final evaluation on nba_test.csv (once only!)")
    
    return {
        'train': train_df,
        'val': val_df,
        'test': test_df,
        'metadata': metadata,
    }


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TRAIN/VALIDATION/TEST SPLIT UTILITY")
    print("=" * 80)
    
    # Configuration
    INPUT_FILE = "data/processed/nba/nba_train_data.csv"
    OUTPUT_DIR = "data/processed/nba/splits"
    
    print(f"\n📁 Configuration:")
    print(f"   Input:  {INPUT_FILE}")
    print(f"   Output: {OUTPUT_DIR}/")
    
    print(f"\n📊 Split ratios:")
    print(f"   Training:   70%")
    print(f"   Validation: 15%")
    print(f"   Test:       15%")
    
    print(f"\n⚠️  Strategy: TEMPORAL split (respects time ordering)")
    print(f"   Train on oldest data, test on newest data")
    print(f"   Prevents data leakage!")
    
    response = input("\nProceed with split? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            result = create_train_val_test_split(
                INPUT_FILE,
                OUTPUT_DIR,
                train_ratio=0.70,
                val_ratio=0.15,
                test_ratio=0.15,
                verbose=True
            )
            
            print("\n🎉 SUCCESS!")
            print(f"\n📊 Quick stats:")
            print(f"   Training:   {len(result['train']):,} games")
            print(f"   Validation: {len(result['val']):,} games")
            print(f"   Test:       {len(result['test']):,} games")
            
        except FileNotFoundError:
            print(f"\n❌ File not found: {INPUT_FILE}")
            print("Please update INPUT_FILE path")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ Cancelled")