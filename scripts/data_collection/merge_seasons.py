"""
Merge Multiple Season Datasets into One
=========================================

Use this when you've collected seasons separately and need to combine them.

Example:
- nba_stats_2022_23.csv
- nba_stats_2023_24.csv  
- nba_stats_2024_25.csv
- nba_stats_2025_26.csv

→ nba_stats_all_seasons.csv
"""

import pandas as pd
import os

# ============================================================
# CONFIGURATION
# ============================================================

# Directory where your season files are
INPUT_DIR = 'data/raw/nba'

# Input files (add/remove as needed)
INPUT_FILES = [
    'nba_stats_2022_23.csv',
    'nba_stats_2023_24.csv',
    'nba_stats_2024_25.csv',
    'nba_stats_2025_26.csv',
    # Add more files here
]

# Output file name
OUTPUT_FILE = 'nba_stats_all_data.csv'

# ============================================================
# MERGE FUNCTION
# ============================================================

def merge_season_files():
    """
    Merge multiple season CSV files into one
    """
    print("="*70)
    print("MERGING SEASON DATASETS")
    print("="*70)
    
    all_data = []
    total_records = 0
    
    # Load each file
    for i, filename in enumerate(INPUT_FILES, 1):
        filepath = os.path.join(INPUT_DIR, filename)
        
        print(f"\n[{i}/{len(INPUT_FILES)}] Loading {filename}...")
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"   ❌ File not found: {filepath}")
            print(f"   Skipping...")
            continue
        
        # Load CSV
        try:
            df = pd.read_csv(filepath)
            records = len(df)
            total_records += records
            
            # Get info
            seasons = df['SEASON'].unique() if 'SEASON' in df.columns else ['Unknown']
            dates = f"{df['GAME_DATE'].min()} to {df['GAME_DATE'].max()}" if 'GAME_DATE' in df.columns else 'Unknown'
            stat_types = df['STAT_TYPE'].unique() if 'STAT_TYPE' in df.columns else ['Unknown']
            
            print(f"   ✅ {records:,} records")
            print(f"      Seasons: {', '.join(seasons)}")
            print(f"      Dates: {dates}")
            print(f"      Stat types: {', '.join(stat_types)}")
            
            all_data.append(df)
            
        except Exception as e:
            print(f"   ❌ Error loading file: {e}")
            continue
    
    # Check if we have data
    if not all_data:
        print("\n❌ No data to merge!")
        return
    
    # Merge all dataframes
    print("\n" + "="*70)
    print("MERGING...")
    print("="*70)
    
    merged_df = pd.concat(all_data, ignore_index=True)
    
    # Convert GAME_DATE to datetime (handle mixed types)
    if 'GAME_DATE' in merged_df.columns:
        print("\n[PROCESSING] Converting GAME_DATE to datetime...")
        merged_df['GAME_DATE'] = pd.to_datetime(merged_df['GAME_DATE'], errors='coerce')
        
        # Check for invalid dates
        invalid_dates = merged_df['GAME_DATE'].isna().sum()
        if invalid_dates > 0:
            print(f"   ⚠️  Found {invalid_dates} invalid dates (will be excluded from date stats)")
    
    print(f"\n✅ Merged {len(INPUT_FILES)} files")
    print(f"   Total records: {len(merged_df):,}")
    
    # Check for duplicates
    print("\n[CHECK] Checking for duplicates...")
    
    if 'TEAM_ID' in merged_df.columns and 'GAME_DATE' in merged_df.columns and 'STAT_TYPE' in merged_df.columns:
        # Ensure GAME_DATE is string for duplicate check (more reliable)
        check_df = merged_df.copy()
        check_df['GAME_DATE'] = check_df['GAME_DATE'].astype(str)
        
        duplicate_check = check_df.duplicated(subset=['TEAM_ID', 'GAME_DATE', 'STAT_TYPE'], keep=False)
        num_duplicates = duplicate_check.sum()
        
        if num_duplicates > 0:
            print(f"   ⚠️  Found {num_duplicates} duplicate records")
            print(f"   Removing duplicates...")
            
            # Remove duplicates from original merged_df
            merged_df['GAME_DATE_STR'] = merged_df['GAME_DATE'].astype(str)
            merged_df = merged_df.drop_duplicates(subset=['TEAM_ID', 'GAME_DATE_STR', 'STAT_TYPE'], keep='first')
            merged_df = merged_df.drop(columns=['GAME_DATE_STR'])
            
            print(f"   ✅ After deduplication: {len(merged_df):,} records")
        else:
            print(f"   ✅ No duplicates found")
    else:
        print("   ⚠️  Cannot check duplicates (missing required columns)")
    
    # Summary statistics
    print("\n" + "="*70)
    print("MERGED DATASET SUMMARY")
    print("="*70)
    
    if 'SEASON' in merged_df.columns:
        print("\n📅 Records by Season:")
        season_counts = merged_df.groupby('SEASON').size().sort_index()
        for season, count in season_counts.items():
            print(f"   {season}: {count:,} records")
    
    if 'STAT_TYPE' in merged_df.columns:
        print("\n📊 Records by Stat Type:")
        stat_counts = merged_df.groupby('STAT_TYPE').size()
        for stat_type, count in stat_counts.items():
            print(f"   {stat_type}: {count:,} records")
    
    if 'GAME_DATE' in merged_df.columns:
        print(f"\n📆 Date Range:")
        valid_dates = merged_df['GAME_DATE'].dropna()
        if len(valid_dates) > 0:
            print(f"   First: {valid_dates.min().strftime('%Y-%m-%d')}")
            print(f"   Last: {valid_dates.max().strftime('%Y-%m-%d')}")
            print(f"   Unique dates: {valid_dates.nunique()}")
        else:
            print(f"   ⚠️  No valid dates found")
    
    if 'TEAM_ID' in merged_df.columns:
        print(f"\n🏀 Teams:")
        print(f"   Unique teams: {merged_df['TEAM_ID'].nunique()}")
    
    print(f"\n📏 Dimensions:")
    print(f"   Rows: {len(merged_df):,}")
    print(f"   Columns: {len(merged_df.columns)}")
    
    # Save merged file
    print("\n" + "="*70)
    print("SAVING MERGED FILE")
    print("="*70)
    
    # Convert GAME_DATE to string format for CSV (prevents Excel date issues)
    if 'GAME_DATE' in merged_df.columns:
        merged_df['GAME_DATE'] = merged_df['GAME_DATE'].dt.strftime('%Y-%m-%d')
    
    output_path = os.path.join(INPUT_DIR, OUTPUT_FILE)
    merged_df.to_csv(output_path, index=False)
    
    print(f"\n✅ Saved: {output_path}")
    print(f"   Size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")
    
    print("\n" + "="*70)
    print("✅ MERGE COMPLETE!")
    print("="*70)

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    merge_season_files()