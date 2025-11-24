"""
Clean Up Duplicate Columns After Merge
=======================================

Removes redundant columns from merged Advanced + Four Factors dataset
"""

import pandas as pd
import os

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = 'data/raw/nba'
INPUT_FILE = 'nba_stats_all_data.csv'
OUTPUT_FILE = 'nba_stats_all_data_cleaned.csv'

# ============================================================
# CLEAN FUNCTION
# ============================================================

def clean_duplicate_columns():
    """
    Remove duplicate columns, keeping only necessary ones
    """
    print("="*70)
    print("CLEANING DUPLICATE COLUMNS")
    print("="*70)
    
    filepath = os.path.join(INPUT_DIR, INPUT_FILE)
    
    # Load data
    print(f"\n[LOADING] {INPUT_FILE}...")
    df = pd.read_csv(filepath)
    print(f"✅ Loaded {len(df):,} records, {len(df.columns)} columns")
    
    # Define columns to DROP (the redundant ones)
    columns_to_drop = []
    
    # 1. Drop Four Factors versions of metadata (keep Advanced versions)
    print("\n[STEP 1] Removing metadata duplicates...")
    metadata_duplicates = [
        'TEAM_NAME_FF',      # Keep TEAM_NAME_ADV
        'GP_FF',             # Keep GP_ADV
        'W_FF',              # Keep W_ADV
        'L_FF',              # Keep L_ADV
        'W_PCT_FF',          # Keep W_PCT_ADV
        'MIN_FF',            # Keep MIN_ADV
        'STAT_TYPE_FF',      # Drop both
        'STAT_TYPE_ADV',     # Drop both
    ]
    columns_to_drop.extend(metadata_duplicates)
    print(f"   Removing {len(metadata_duplicates)} metadata columns")
    
    # 2. Drop Advanced versions of statistical duplicates
    #    (These are SAME metrics - keep 4F version)
    print("\n[STEP 2] Removing statistical duplicates...")
    stat_duplicates = [
        'EFG_PCT_ADV',        # Keep EFG_PCT_FF (same value)
        'TM_TOV_PCT_ADV',     # Keep TM_TOV_PCT_FF (same value)
        'OREB_PCT_ADV',       # Keep OREB_PCT_FF (same value)
    ]
    columns_to_drop.extend(stat_duplicates)
    print(f"   Removing {len(stat_duplicates)} stat metric columns")
    
    # 3. Drop ranking duplicates
    print("\n[STEP 3] Removing ranking duplicates...")
    ranking_duplicates = [
        'GP_RANK_FF',
        'W_RANK_FF',
        'L_RANK_FF',
        'W_PCT_RANK_FF',
        'MIN_RANK_FF',
        'EFG_PCT_RANK_ADV',
        'TM_TOV_PCT_RANK_ADV',
        'OREB_PCT_RANK_ADV',
    ]
    columns_to_drop.extend(ranking_duplicates)
    print(f"   Removing {len(ranking_duplicates)} ranking columns")
    
    # Check which columns actually exist in the dataframe
    existing_drops = [col for col in columns_to_drop if col in df.columns]
    missing_drops = [col for col in columns_to_drop if col not in df.columns]
    
    if missing_drops:
        print(f"\n⚠️  {len(missing_drops)} columns not found (already removed?):")
        for col in missing_drops[:5]:  # Show first 5
            print(f"   - {col}")
    
    # Drop the columns
    print(f"\n[DROPPING] Removing {len(existing_drops)} duplicate columns...")
    df_cleaned = df.drop(columns=existing_drops)
    
    # Rename _ADV suffixes to remove suffix (cleaner names)
    print("\n[RENAMING] Removing _ADV suffixes...")
    rename_map = {}
    for col in df_cleaned.columns:
        if col.endswith('_ADV'):
            new_name = col[:-4]  # Remove last 4 chars (_ADV)
            rename_map[col] = new_name
    
    df_cleaned = df_cleaned.rename(columns=rename_map)
    print(f"   Renamed {len(rename_map)} columns")
    
    # Summary
    print("\n" + "="*70)
    print("CLEANING SUMMARY")
    print("="*70)
    
    print(f"\n📊 BEFORE:")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Records: {len(df):,}")
    
    print(f"\n📊 AFTER:")
    print(f"   Columns: {len(df_cleaned.columns)}")
    print(f"   Records: {len(df_cleaned):,}")
    print(f"   Removed: {len(df.columns) - len(df_cleaned.columns)} columns")
    
    # Show final columns by category
    print(f"\n📋 FINAL COLUMN CATEGORIES:")
    
    # ID/Metadata
    id_cols = [c for c in df_cleaned.columns if c in ['TEAM_ID', 'TEAM_NAME', 'GAME_DATE', 'SEASON', 'STAT_TYPE']]
    print(f"\n   ID/Metadata ({len(id_cols)}):")
    for col in id_cols:
        print(f"      - {col}")
    
    # Record metadata
    record_cols = [c for c in df_cleaned.columns if c in ['GP', 'W', 'L', 'W_PCT', 'MIN']]
    print(f"\n   Record/Playing Time ({len(record_cols)}):")
    for col in record_cols:
        print(f"      - {col}")
    
    # Advanced Stats (no suffix)
    advanced_metrics = [c for c in df_cleaned.columns 
                       if c in ['OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE', 'AST_PCT', 
                               'AST_TO', 'AST_RATIO', 'DREB_PCT', 'REB_PCT', 'TS_PCT', 'PIE',
                               'EFG_PCT', 'TM_TOV_PCT', 'OREB_PCT']]
    print(f"\n   Advanced Metrics ({len(advanced_metrics)}):")
    for col in sorted(advanced_metrics):
        print(f"      - {col}")
    
    # Four Factors unique (with _FF suffix still)
    ff_metrics = [c for c in df_cleaned.columns 
                 if c in ['FTA_RATE', 'OPP_EFG_PCT', 'OPP_FTA_RATE', 'OPP_TOV_PCT', 'OPP_OREB_PCT']]
    print(f"\n   Four Factors Metrics ({len(ff_metrics)}):")
    for col in sorted(ff_metrics):
        print(f"      - {col}")
    
    # Rankings
    rank_cols = [c for c in df_cleaned.columns if '_RANK' in c]
    print(f"\n   Rankings ({len(rank_cols)}):")
    for col in sorted(rank_cols)[:10]:  # Show first 10
        print(f"      - {col}")
    if len(rank_cols) > 10:
        print(f"      ... and {len(rank_cols) - 10} more")
    
    # Save cleaned data
    print("\n" + "="*70)
    print("SAVING CLEANED DATA")
    print("="*70)
    
    output_path = os.path.join(INPUT_DIR, OUTPUT_FILE)
    df_cleaned.to_csv(output_path, index=False)
    
    print(f"\n✅ Saved: {output_path}")
    print(f"   Size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
    
    # Show space saved
    input_size = os.path.getsize(filepath) / (1024*1024)
    output_size = os.path.getsize(output_path) / (1024*1024)
    savings = input_size - output_size
    savings_pct = (savings / input_size) * 100
    
    print(f"\n💾 SPACE SAVED:")
    print(f"   Original: {input_size:.1f} MB")
    print(f"   Cleaned: {output_size:.1f} MB")
    print(f"   Saved: {savings:.1f} MB ({savings_pct:.1f}%)")
    
    print("\n" + "="*70)
    print("✅ CLEANING COMPLETE!")
    print("="*70)
    print(f"\n💡 Your cleaned file: {OUTPUT_FILE}")
    print(f"   Use this for feature engineering and modeling")

if __name__ == "__main__":
    clean_duplicate_columns()