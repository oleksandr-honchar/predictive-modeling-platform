"""
Hybrid Approach: Official Advanced Stats + Rolling Windows
Created: 2025-11-24

STRATEGY:
    1. Fetch official season-to-date advanced stats from NBA API
    2. Calculate last-5 and last-10 rolling windows from game data
    3. Combine both into single dataset

ADVANTAGES:
    - Official NBA calculations for main stats (accurate)
    - Fast execution (~7 minutes vs 2 hours)
    - Minimal API calls (~400 vs 12,000)
    - Best of both worlds!

INPUT:
    data/raw/nba/nba_games_all_data.csv

OUTPUT:
    data/processed/nba/team_stats_hybrid.csv
"""

import pandas as pd
import numpy as np
from nba_api.stats.endpoints import leaguedashteamstats
from datetime import datetime, timedelta
import time
import os

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = 'data/raw/nba/nba_games_all_data.csv'
OUTPUT_DIR = 'data/processed/nba'
OUTPUT_FILE = 'team_stats_hybrid.csv'
RATE_LIMIT_DELAY = 0.6  # seconds between API calls

# ============================================================
# PART 1: FETCH OFFICIAL ADVANCED STATS FROM API
# ============================================================

def get_season_start_date(season):
    """Get typical season start date for a season"""
    season_starts = {
        '2022-23': '2022-10-18',
        '2023-24': '2023-10-24',
        '2024-25': '2024-10-22',
        '2025-26': '2025-10-21',
    }
    return season_starts.get(season, None)

def fetch_advanced_stats_for_date(season, date_str, retry_attempt=0):
    """
    Fetch advanced stats for ALL teams up to a specific date
    
    Args:
        season: Season string (e.g., '2023-24')
        date_str: Date string in 'YYYY-MM-DD' format
        retry_attempt: Current retry attempt number
    
    Returns:
        DataFrame with advanced stats for all 30 teams
    """
    try:
        # Convert date format for API (MM/DD/YYYY)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        api_date = date_obj.strftime('%m/%d/%Y')
        season_start = get_season_start_date(season)
        season_start_api = datetime.strptime(season_start, '%Y-%m-%d').strftime('%m/%d/%Y')
        
        # Rate limiting (longer for retries)
        if retry_attempt > 0:
            time.sleep(RATE_LIMIT_DELAY * 2)
        else:
            time.sleep(RATE_LIMIT_DELAY)
        
        # Fetch advanced stats
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season=season,
            date_from_nullable=season_start_api,
            date_to_nullable=api_date,
            measure_type_detailed_defense='Advanced',
            season_type_all_star='Regular Season',
            timeout=60  # Longer timeout for retries
        )
        
        df = stats.get_data_frames()[0]
        
        # Add date for tracking
        df['AS_OF_DATE'] = date_str
        
        return df
        
    except Exception as e:
        if retry_attempt == 0:
            print(f"Error fetching stats for {season} on {date_str}: {e}")
        return pd.DataFrame()

def collect_all_advanced_stats(games_df):
    """
    Collect advanced stats for all unique game dates
    
    Args:
        games_df: DataFrame with game data
    
    Returns:
        Tuple of (DataFrame with advanced stats, list of failed (season, date) tuples)
    """
    print("\n" + "="*70)
    print("FETCHING OFFICIAL ADVANCED STATS FROM NBA API")
    print("="*70)
    
    # Get unique dates per season
    games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
    unique_dates = games_df.groupby('SEASON')['GAME_DATE'].unique()
    
    all_stats = []
    failed_dates = []
    total_calls = sum(len(dates) for dates in unique_dates)
    current_call = 0
    
    print(f"\nTotal API calls needed: {total_calls}")
    print(f"Estimated time: {total_calls * RATE_LIMIT_DELAY / 60:.1f} minutes\n")
    
    for season, dates in unique_dates.items():
        print(f"\n{'='*70}")
        print(f"Season: {season} ({len(dates)} unique game dates)")
        print(f"{'='*70}")
        
        for date in sorted(dates):
            current_call += 1
            date_str = date.strftime('%Y-%m-%d')
            
            print(f"[{current_call}/{total_calls}] Fetching {date_str}...", end=" ")
            
            stats_df = fetch_advanced_stats_for_date(season, date_str)
            
            if not stats_df.empty:
                stats_df['SEASON'] = season
                all_stats.append(stats_df)
                print(f"✅ Got {len(stats_df)} teams")
            else:
                failed_dates.append((season, date_str))
                print("❌ Failed")
    
    if all_stats:
        combined = pd.concat(all_stats, ignore_index=True)
        print(f"\n✅ Collected {len(combined):,} total records")
        print(f"⚠️  Failed dates: {len(failed_dates)}")
        return combined, failed_dates
    else:
        print("\n❌ No stats collected")
        return pd.DataFrame(), failed_dates

# ============================================================
# PART 2: CALCULATE ROLLING WINDOWS FROM GAME DATA
# ============================================================

def calculate_rolling_windows(games_df):
    """
    Calculate last-5 and last-10 game rolling averages
    
    Args:
        games_df: DataFrame with game-level data
    
    Returns:
        DataFrame with rolling window statistics
    """
    print("\n" + "="*70)
    print("CALCULATING ROLLING WINDOWS (LAST 5 & LAST 10)")
    print("="*70)
    
    # Sort by team and date
    games_df = games_df.sort_values(['TEAM_ABBR', 'GAME_DATE']).reset_index(drop=True)
    
    # Stats to calculate
    stats_columns = [
        'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
        'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST',
        'STL', 'BLK', 'TOV', 'PF'
    ]
    
    # Group by team and season
    grouped = games_df.groupby(['TEAM_ABBR', 'SEASON'])
    
    # Calculate last 5 games
    print("\nCalculating last 5 game averages...")
    for col in stats_columns:
        if col in games_df.columns:
            games_df[f'last_5_{col}'] = grouped[col].transform(
                lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
            )
    
    # Calculate last 10 games
    print("Calculating last 10 game averages...")
    for col in stats_columns:
        if col in games_df.columns:
            games_df[f'last_10_{col}'] = grouped[col].transform(
                lambda x: x.shift(1).rolling(window=10, min_periods=1).mean()
            )
    
    print("✅ Rolling windows calculated")
    
    return games_df

# ============================================================
# PART 2.5: RETRY FAILED DATES AND INTERPOLATION
# ============================================================

def retry_failed_dates(failed_list, max_retries=2):
    """
    Retry dates that failed during initial collection
    
    Args:
        failed_list: List of (season, date_str) tuples that failed
        max_retries: Number of retry attempts
    
    Returns:
        List of successfully fetched DataFrames
    """
    if not failed_list:
        return []
    
    print("\n" + "="*70)
    print(f"RETRYING {len(failed_list)} FAILED DATES")
    print("="*70)
    
    recovered_stats = []
    
    for season, date_str in failed_list:
        success = False
        
        for attempt in range(max_retries):
            print(f"[Attempt {attempt+1}/{max_retries}] {season} on {date_str}...", end=" ")
            
            stats_df = fetch_advanced_stats_for_date(season, date_str, retry_attempt=attempt+1)
            
            if not stats_df.empty:
                print(f"✅ Recovered! Got {len(stats_df)} teams")
                stats_df['SEASON'] = season
                recovered_stats.append(stats_df)
                success = True
                break
            else:
                print("❌ Still failed")
        
        if not success:
            print(f"⚠️  Could not recover {date_str} after {max_retries} attempts")
    
    print(f"\n✅ Recovered {len(recovered_stats)} out of {len(failed_list)} dates")
    return recovered_stats

def interpolate_missing_stats(df):
    """
    Interpolate missing advanced stats using linear interpolation
    
    Args:
        df: DataFrame with potential missing values
    
    Returns:
        DataFrame with interpolated values
    """
    print("\n" + "="*70)
    print("CHECKING FOR MISSING VALUES")
    print("="*70)
    
    # Count missing before
    missing_before = df['season_OFF_RATING'].isna().sum()
    print(f"Missing values found: {missing_before}")
    
    if missing_before == 0:
        print("✅ No missing values - dataset is complete!")
        return df
    
    print("\nInterpolating missing values...")
    
    # Sort by team and date
    df = df.sort_values(['TEAM_ABBR', 'GAME_DATE']).reset_index(drop=True)
    
    # Columns to interpolate
    numeric_cols = [
        'season_OFF_RATING', 'season_DEF_RATING', 
        'season_NET_RATING', 'season_PACE', 'season_W_PCT'
    ]
    
    # Interpolate for each team
    for team in df['TEAM_ABBR'].unique():
        team_mask = df['TEAM_ABBR'] == team
        
        for col in numeric_cols:
            if col in df.columns:
                df.loc[team_mask, col] = df.loc[team_mask, col].interpolate(
                    method='linear',
                    limit_direction='both'
                )
    
    # Count missing after
    missing_after = df['season_OFF_RATING'].isna().sum()
    print(f"Missing values after interpolation: {missing_after}")
    print(f"✅ Interpolated {missing_before - missing_after} values")
    
    return df

# ============================================================
# PART 3: MERGE OFFICIAL STATS WITH ROLLING WINDOWS
# ============================================================

def merge_stats(games_df, api_stats_df):
    """
    Merge official API stats with game data and rolling windows
    
    Args:
        games_df: DataFrame with game data and rolling windows
        api_stats_df: DataFrame with official advanced stats from API
    
    Returns:
        Final merged DataFrame
    """
    print("\n" + "="*70)
    print("MERGING OFFICIAL STATS WITH ROLLING WINDOWS")
    print("="*70)
    
    # Debug: Check what columns we have
    print(f"\nAPI stats columns: {api_stats_df.columns.tolist()[:10]}...")
    print(f"Games columns: {games_df.columns.tolist()[:10]}...")
    
    # Rename AS_OF_DATE to GAME_DATE if it exists
    if 'AS_OF_DATE' in api_stats_df.columns:
        api_stats_df = api_stats_df.rename(columns={'AS_OF_DATE': 'GAME_DATE'})
        print("Renamed AS_OF_DATE to GAME_DATE")
    
    # Convert dates to datetime
    api_stats_df['GAME_DATE'] = pd.to_datetime(api_stats_df['GAME_DATE'])
    games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
    
    # Determine merge keys based on available columns
    # Best option: Use TEAM_ID (both have it!)
    if 'TEAM_ID' in api_stats_df.columns and 'TEAM_ID' in games_df.columns:
        merge_keys = ['TEAM_ID', 'GAME_DATE', 'SEASON']
        print(f"\n✅ Using TEAM_ID for merge (most reliable)")
    else:
        print(f"\n❌ Error: Cannot find common team identifier")
        return games_df
    
    # Select stats we want from API
    stat_cols = ['OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE', 'W', 'L', 'W_PCT']
    available_stats = [col for col in stat_cols if col in api_stats_df.columns]
    
    merge_cols = merge_keys + available_stats
    api_subset = api_stats_df[merge_cols].copy()
    
    print(f"Selected API stats: {available_stats}")
    
    # Rename stats to indicate they're season-to-date
    stat_rename = {
        'OFF_RATING': 'season_OFF_RATING',
        'DEF_RATING': 'season_DEF_RATING',
        'NET_RATING': 'season_NET_RATING',
        'PACE': 'season_PACE',
        'W_PCT': 'season_W_PCT',
        'W': 'season_W',
        'L': 'season_L'
    }
    api_subset = api_subset.rename(columns={k: v for k, v in stat_rename.items() if k in api_subset.columns})
    
    print(f"\nMerging {len(games_df):,} game records with {len(api_subset):,} API records...")
    print(f"Merge keys: {merge_keys}")
    
    # Merge
    merged = games_df.merge(
        api_subset,
        on=merge_keys,
        how='left'
    )
    
    print(f"✅ Merged dataset created: {len(merged):,} records")
    
    # Check merge quality
    if 'season_OFF_RATING' in merged.columns:
        missing = merged['season_OFF_RATING'].isna().sum()
        matched = len(merged) - missing
        pct = (matched / len(merged)) * 100
        print(f"Merge success rate: {pct:.1f}% ({matched:,} / {len(merged):,} matched)")
        
        if missing > 0:
            print(f"⚠️  {missing:,} records without API stats (will be interpolated)")
    
    return merged

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """
    Main hybrid processing workflow with retry and interpolation
    """
    start_time = datetime.now()
    print("\n" + "="*70)
    print("HYBRID APPROACH: OFFICIAL STATS + ROLLING WINDOWS")
    print("="*70)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Load game data
    print("\n[STEP 1] Loading game data...")
    games_df = pd.read_csv(INPUT_FILE)
    print(f"✅ Loaded {len(games_df):,} game records")
    
    # Step 2: Fetch official advanced stats from API
    print("\n[STEP 2] Fetching official advanced stats from NBA API...")
    api_stats_df, failed_dates = collect_all_advanced_stats(games_df)
    
    # Step 2.5: Retry failed dates
    if failed_dates:
        print(f"\n⚠️  {len(failed_dates)} dates failed. Attempting recovery...")
        recovered = retry_failed_dates(failed_dates, max_retries=2)
        if recovered:
            api_stats_df = pd.concat([api_stats_df] + recovered, ignore_index=True)
            print(f"✅ Total records after recovery: {len(api_stats_df):,}")
    
    # Step 3: Calculate rolling windows
    print("\n[STEP 3] Calculating rolling windows...")
    games_with_rolling = calculate_rolling_windows(games_df)
    
    # Step 4: Merge everything
    print("\n[STEP 4] Merging official stats with rolling windows...")
    final_df = merge_stats(games_with_rolling, api_stats_df)
    
    # Step 4.5: Interpolate any remaining missing values
    if 'season_OFF_RATING' in final_df.columns:
        final_df = interpolate_missing_stats(final_df)
    
    # Step 5: Save
    print("\n[STEP 5] Saving final dataset...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    final_df.to_csv(output_path, index=False)
    
    print(f"\n{'='*70}")
    print(f"✅ Data saved successfully!")
    print(f"📁 Location: {output_path}")
    print(f"📊 Total records: {len(final_df):,}")
    print(f"📅 Columns: {len(final_df.columns)}")
    
    # Data completeness check
    if 'season_OFF_RATING' in final_df.columns:
        missing_count = final_df['season_OFF_RATING'].isna().sum()
        if missing_count == 0:
            print(f"✅ Data completeness: 100% (no missing values)")
        else:
            print(f"⚠️  Remaining missing values: {missing_count}")
    
    print(f"{'='*70}")
    
    # Summary
    print("\n[SUMMARY] Available Statistics:")
    print("\n✅ Official NBA Advanced Stats (from API):")
    print("   - season_OFF_RATING, season_DEF_RATING, season_NET_RATING")
    print("   - season_PACE, season_W_PCT")
    
    print("\n✅ Rolling Window Stats (calculated):")
    print("   - last_5_PTS, last_5_FG_PCT, last_5_AST, etc.")
    print("   - last_10_PTS, last_10_FG_PCT, last_10_AST, etc.")
    
    print("\n✅ Raw Game Data:")
    print("   - All original game statistics")
    
    # Completion
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n⏱️  Total execution time: {duration}")
    print(f"✅ Hybrid data collection complete!")

if __name__ == "__main__":
    main()