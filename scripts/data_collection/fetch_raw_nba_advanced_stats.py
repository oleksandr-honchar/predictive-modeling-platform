"""
Day-by-Day Raw NBA Stats Collection (No Date Adjustments)
Created: 2025-11-24

PURPOSE:
    Collect advanced stats for each game date
    API returns stats "as of" that date (includes games played up to that date)
    NO adjustments, NO logic, just collect what API gives us

OUTPUT:
    data/raw/nba/nba_stats_by_date_raw.csv
"""

from nba_api.stats.endpoints import leaguedashteamstats
import pandas as pd
import time
from datetime import datetime
import os

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = 'data/raw/nba/nba_games_data.csv'
OUTPUT_DIR = 'data/raw/nba'
OUTPUT_FILE = 'nba_stats_2021-22.csv'
RATE_LIMIT_DELAY = 1.0  # Increased from 0.6 to prevent rate limiting

# SEASONS TO COLLECT (None = all seasons in game data)
SEASONS = ['2021-22']  # Edit this list
# SEASONS = None  # Uncomment to collect all seasons

# COLLECT ONLY TEAMS THAT PLAYED ON EACH DATE
# True = Only teams that played (faster, less data)
# False = All 30 teams for each date (more data)
ONLY_TEAMS_THAT_PLAYED = True

# ============================================================
# SIMPLE FETCH FUNCTION
# ============================================================

def fetch_stats_for_date(season, date_str, team_ids=None, stat_type='Advanced', max_retries=3):
    """
    Fetch stats for a specific date - NO adjustments
    INCLUDES AUTOMATIC RETRY on failures
    
    Just asks API: "Give me stats as of this date"
    Whatever API returns, we keep
    
    Args:
        season: Season string (e.g., '2022-23')
        date_str: Date in 'YYYY-MM-DD' format
        team_ids: List of team IDs to filter (None = all teams)
        stat_type: 'Advanced' or 'Four Factors'
        max_retries: Number of retry attempts (default: 3)
    
    Returns:
        DataFrame with stats as API provides them
    """
    for attempt in range(max_retries):
        try:
            # Convert to API format (MM/DD/YYYY)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            api_date = date_obj.strftime('%m/%d/%Y')
            
            # Rate limiting (longer wait for retries)
            if attempt > 0:
                wait_time = RATE_LIMIT_DELAY * (2 ** attempt)  # Exponential backoff
                time.sleep(wait_time)
            else:
                time.sleep(RATE_LIMIT_DELAY)
            
            # Fetch stats - Advanced or Four Factors
            stats = leaguedashteamstats.LeagueDashTeamStats(
                season=season,
                date_to_nullable=api_date,  # Just "up to this date"
                measure_type_detailed_defense=stat_type,
                season_type_all_star='Regular Season',
                timeout=90
            )
            
            df = stats.get_data_frames()[0]
            
            # Filter to only teams that played if specified
            if team_ids is not None:
                df = df[df['TEAM_ID'].isin(team_ids)]
            
            # Add metadata
            df['GAME_DATE'] = date_str
            df['SEASON'] = season
            df['STAT_TYPE'] = stat_type
            
            return df, None  # Success!
            
        except Exception as e:
            error_msg = str(e)
            
            # If this was the last attempt, return error
            if attempt == max_retries - 1:
                return pd.DataFrame(), error_msg
            
            # Otherwise, we'll retry (loop continues)
            continue
    
    return pd.DataFrame(), "Max retries exceeded"

# ============================================================
# COLLECTION
# ============================================================

def collect_all_dates(games_df, stat_type='Advanced'):
    """
    Collect stats for each unique game date
    INCLUDES CHECKPOINT SAVING and RESUME CAPABILITY
    
    Args:
        games_df: DataFrame with game data
        stat_type: 'Advanced' or 'Four Factors'
    """
    print("\n" + "="*70)
    print(f"DAY-BY-DAY COLLECTION: {stat_type.upper()}")
    print("="*70)
    
    # Check for existing checkpoint
    checkpoint_file = OUTPUT_FILE.replace('.csv', f'_checkpoint_{stat_type}.csv')
    checkpoint_path = os.path.join(OUTPUT_DIR, checkpoint_file)
    
    if os.path.exists(checkpoint_path):
        print(f"\n⚠️  Found checkpoint file: {checkpoint_file}")
        existing_df = pd.read_csv(checkpoint_path)
        print(f"   Contains: {len(existing_df):,} records")
        print(f"   Last date: {existing_df['GAME_DATE'].max()}")
        
        resume = input("\n   Resume from checkpoint? (y/n): ").strip().lower()
        if resume == 'y':
            all_stats = [existing_df]
            # Get dates already collected
            collected_dates = set(existing_df['GAME_DATE'].unique())
            print(f"   ✅ Resuming... {len(collected_dates)} dates already collected")
        else:
            all_stats = []
            collected_dates = set()
            print("   Starting fresh collection...")
    else:
        all_stats = []
        collected_dates = set()
    
    print("\nWhat this does:")
    print("- For each game date, ask API: 'stats as of this date'")
    if ONLY_TEAMS_THAT_PLAYED:
        print("- Collect ONLY teams that played on that date")
    else:
        print("- Collect ALL 30 teams for each date")
    print("- Keep whatever API returns")
    print("- NO logic about season start, day before, etc.")
    print("- AUTOMATIC RETRY on failures (up to 3 attempts)")
    print("- 💾 CHECKPOINT SAVING every 50 dates")
    
    # Get unique dates per season
    games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
    unique_dates = games_df.groupby('SEASON')['GAME_DATE'].unique()
    
    all_stats = []
    failed_dates = []
    retry_count = 0
    total_calls = sum(len(dates) for dates in unique_dates)
    current_call = 0
    checkpoint_counter = 0
    CHECKPOINT_INTERVAL = 50  # Save every 50 dates
    
    print(f"\nTotal dates: {total_calls}")
    print(f"Estimated time: {total_calls * RATE_LIMIT_DELAY / 60:.1f} minutes")
    print("💡 Press Ctrl+C to stop")
    print("🔄 Automatic retry enabled (3 attempts per date)\n")
    
    for season, dates in unique_dates.items():
        print(f"\n{'='*70}")
        print(f"Season: {season} ({len(dates)} dates)")
        print(f"{'='*70}")
        
        for date in sorted(dates):
            current_call += 1
            date_str = date.strftime('%Y-%m-%d')
            
            # Skip if already collected (resuming from checkpoint)
            if date_str in collected_dates:
                print(f"[{current_call}/{total_calls}] {date_str}... ⏭️  Already collected")
                continue
            
            # Get teams that played on this date (if filtering enabled)
            if ONLY_TEAMS_THAT_PLAYED:
                teams_on_date = games_df[
                    (games_df['GAME_DATE'] == date) & 
                    (games_df['SEASON'] == season)
                ]['TEAM_ID'].unique().tolist()
                team_count = len(teams_on_date)
            else:
                teams_on_date = None
                team_count = 30
            
            print(f"[{current_call}/{total_calls}] {date_str}...", end=" ")
            
            df, error = fetch_stats_for_date(season, date_str, teams_on_date, stat_type, max_retries=3)
            
            if not df.empty:
                all_stats.append(df)
                print(f"✅ {len(df)} teams (expected: {team_count})")
                
                # Checkpoint saving every 50 dates
                checkpoint_counter += 1
                if checkpoint_counter % CHECKPOINT_INTERVAL == 0:
                    checkpoint_file = OUTPUT_FILE.replace('.csv', f'_checkpoint_{stat_type}.csv')
                    checkpoint_path = os.path.join(OUTPUT_DIR, checkpoint_file)
                    temp_df = pd.concat(all_stats, ignore_index=True)
                    temp_df.to_csv(checkpoint_path, index=False)
                    print(f"    💾 Checkpoint saved: {len(temp_df):,} records")
            else:
                # Only truly failed after all retries
                print(f"❌ Failed after 3 attempts")
                failed_dates.append((season, date_str, error))
                retry_count += 2  # Used 2 retries (3 total attempts)
    
    # Combine
    if all_stats:
        combined = pd.concat(all_stats, ignore_index=True)
        print(f"\n✅ Collected {len(combined):,} records")
        print(f"🔄 Retry attempts used: ~{retry_count}")
        print(f"❌ Failed {len(failed_dates)} dates (after retries)")
        return combined, failed_dates
    else:
        print("\n❌ No data collected")
        return pd.DataFrame(), failed_dates

# ============================================================
# MAIN
# ============================================================

def main():
    """
    Main collection workflow - collects BOTH Advanced Stats and Four Factors
    """
    start_time = datetime.now()
    print("\n" + "="*70)
    print("DAY-BY-DAY RAW STATS COLLECTION")
    print("="*70)
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nCollecting:")
    print("  1. Advanced Stats (OFF_RATING, DEF_RATING, NET_RATING, etc.)")
    print("  2. Four Factors (EFG_PCT, TOV_PCT, OREB_PCT, etc.)")
    
    # Load games to get dates
    print("\n[STEP 1] Loading game data...")
    games_df = pd.read_csv(INPUT_FILE)
    print(f"✅ Loaded {len(games_df):,} games")
    
    # Filter by seasons if specified
    if SEASONS is not None:
        print(f"\n📅 Filtering to seasons: {', '.join(SEASONS)}")
        games_df = games_df[games_df['SEASON'].isin(SEASONS)]
        print(f"✅ Filtered to {len(games_df):,} games")
        print(f"   Seasons: {sorted(games_df['SEASON'].unique())}")
    else:
        print(f"📅 Collecting all seasons: {sorted(games_df['SEASON'].unique())}")
    
    # Collect Advanced Stats
    print("\n[STEP 2] Collecting Advanced Stats...")
    advanced_df, failed_adv = collect_all_dates(games_df, stat_type='Advanced')
    
    # Collect Four Factors
    print("\n[STEP 3] Collecting Four Factors...")
    four_factors_df, failed_ff = collect_all_dates(games_df, stat_type='Four Factors')
    
    # Merge both datasets
    if not advanced_df.empty and not four_factors_df.empty:
        print("\n[STEP 4] Merging Advanced Stats and Four Factors...")
        
        # Merge on TEAM_ID, GAME_DATE, SEASON
        merged_df = advanced_df.merge(
            four_factors_df,
            on=['TEAM_ID', 'GAME_DATE', 'SEASON'],
            how='outer',
            suffixes=('_ADV', '_FF')
        )
        
        print(f"✅ Merged: {len(merged_df):,} records")
        
        # Save
        print("\n[STEP 5] Saving...")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        merged_df.to_csv(output_path, index=False)
        
        print(f"\n{'='*70}")
        print(f"✅ SAVED!")
        print(f"{'='*70}")
        print(f"📁 {output_path}")
        print(f"📊 Records: {len(merged_df):,}")
        print(f"📅 Columns: {len(merged_df.columns)}")
        print(f"❌ Failed (Advanced): {len(failed_adv)} dates")
        print(f"❌ Failed (Four Factors): {len(failed_ff)} dates")
        
        # Show columns
        print(f"\n📋 Available columns (first 30):")
        for i, col in enumerate(merged_df.columns.tolist()[:30], 1):
            print(f"   {i}. {col}")
        if len(merged_df.columns) > 30:
            print(f"   ... and {len(merged_df.columns) - 30} more")
        
        # Summary
        print(f"\n📈 Data summary:")
        print(f"   Seasons: {sorted(merged_df['SEASON'].unique())}")
        print(f"   Date range: {merged_df['GAME_DATE'].min()} to {merged_df['GAME_DATE'].max()}")
        print(f"   Unique dates: {merged_df['GAME_DATE'].nunique()}")
        print(f"   Teams: {merged_df['TEAM_ID'].nunique()}")
        
        # Key columns check
        key_cols = ['OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE', 'EFG_PCT', 'TM_TOV_PCT']
        available = [col for col in key_cols if col in merged_df.columns]
        print(f"\n✅ Key columns available: {', '.join(available)}")
        
        print(f"\n{'='*70}")
        
    elif not advanced_df.empty:
        # Only Advanced Stats collected
        print("\n⚠️  Only Advanced Stats collected (Four Factors failed)")
        output_path = os.path.join(OUTPUT_DIR, 'nba_advanced_stats_only.csv')
        advanced_df.to_csv(output_path, index=False)
        print(f"✅ Saved Advanced Stats: {output_path}")
        
    elif not four_factors_df.empty:
        # Only Four Factors collected
        print("\n⚠️  Only Four Factors collected (Advanced Stats failed)")
        output_path = os.path.join(OUTPUT_DIR, 'nba_four_factors_only.csv')
        four_factors_df.to_csv(output_path, index=False)
        print(f"✅ Saved Four Factors: {output_path}")
        
    else:
        print("\n❌ No data collected")
    
    # Failed dates summary
    all_failed = set(failed_adv + failed_ff)
    if all_failed:
        print(f"\n⚠️  FAILED DATES ({len(all_failed)} unique):")
        for season, date, error in list(all_failed)[:10]:
            print(f"   {season} {date}: {error[:50]}...")
        if len(all_failed) > 10:
            print(f"   ... and {len(all_failed) - 10} more")
    
    # Done
    end_time = datetime.now()
    print(f"\n⏱️  Time: {end_time - start_time}")
    print(f"✅ Done!")

if __name__ == "__main__":
    main()