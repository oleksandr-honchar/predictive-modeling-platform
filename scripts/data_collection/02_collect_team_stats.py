"""
Improved Advanced Stats Collection
===================================
Collects team advanced statistics for each game date
Works with matchup-format game data (1 row per game)

Key improvements:
- Works with HOME_TEAM_ID and AWAY_TEAM_ID format
- Better error handling
- Checkpoint saving
- Resume capability
- Collects both Advanced Stats AND Four Factors

INPUT:
    data/raw/nba/nba_games_all_seasons_RAW.csv (from improved collection script)

OUTPUT:
    data/raw/nba/nba_team_stats_by_date.csv
"""

from nba_api.stats.endpoints import leaguedashteamstats
import pandas as pd
import time
from datetime import datetime
import os

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = 'data/raw/nba/nba_games_all_seasons_RAW.csv'
OUTPUT_DIR = 'data/raw/nba'
OUTPUT_FILE = 'nba_team_stats_by_date.csv'
CHECKPOINT_FILE = 'nba_team_stats_checkpoint.csv'

RATE_LIMIT_DELAY = 1.0
CHECKPOINT_INTERVAL = 50  # Save every 50 dates
MAX_RETRIES = 3

# Filter to specific seasons if needed (None = all seasons)
SEASONS_FILTER = None  # e.g., ['2024-25', '2025-26']

# ============================================================
# FETCH FUNCTIONS
# ============================================================

def fetch_stats_for_date(season, date_str, team_ids=None, stat_type='Advanced', max_retries=MAX_RETRIES):
    """
    Fetch team statistics as of a specific date.
    
    Args:
        season (str): Season like '2024-25'
        date_str (str): Date in 'YYYY-MM-DD' format
        team_ids (list): Optional list of team IDs to filter for (saves API data)
        stat_type (str): 'Advanced' or 'Four Factors'
        max_retries (int): Number of retry attempts
    
    Returns:
        tuple: (DataFrame with stats, error message if failed)
    """
    for attempt in range(max_retries):
        try:
            # Convert to API format
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            api_date = date_obj.strftime('%m/%d/%Y')
            
            # Rate limiting with exponential backoff
            wait_time = RATE_LIMIT_DELAY * (2 ** attempt) if attempt > 0 else RATE_LIMIT_DELAY
            time.sleep(wait_time)
            
            # Fetch stats
            stats = leaguedashteamstats.LeagueDashTeamStats(
                season=season,
                date_to_nullable=api_date,
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
            
            return df, None
            
        except Exception as e:
            if attempt == max_retries - 1:
                return pd.DataFrame(), str(e)
            continue
    
    return pd.DataFrame(), "Max retries exceeded"


def merge_advanced_and_four_factors(adv_df, ff_df):
    """
    Merge Advanced Stats and Four Factors datasets.
    
    Args:
        adv_df: DataFrame with Advanced stats
        ff_df: DataFrame with Four Factors stats
    
    Returns:
        DataFrame: Merged stats
    """
    if adv_df.empty or ff_df.empty:
        return adv_df if not adv_df.empty else ff_df
    
    # Merge on TEAM_ID, GAME_DATE, SEASON
    merged = adv_df.merge(
        ff_df,
        on=['TEAM_ID', 'GAME_DATE', 'SEASON'],
        how='outer',
        suffixes=('', '_FF')
    )
    
    # Remove duplicate columns
    duplicate_cols = [col for col in merged.columns if col.endswith('_FF')]
    
    for col in duplicate_cols:
        base_col = col.replace('_FF', '')
        if base_col in merged.columns:
            # Keep the original, drop the duplicate
            merged = merged.drop(columns=[col])
    
    return merged


# ============================================================
# COLLECTION
# ============================================================

def collect_stats_for_all_dates(games_df):
    """
    Collect stats for all unique game dates with checkpoint support.
    OPTIMIZATION: Only collects stats for teams that played on each date.
    
    Args:
        games_df (pd.DataFrame): Game data with GAME_DATE and SEASON columns
    
    Returns:
        pd.DataFrame: Combined stats for all dates
    """
    checkpoint_path = os.path.join(OUTPUT_DIR, CHECKPOINT_FILE)
    
    # Check for checkpoint
    collected_dates = set()
    all_stats = []
    
    if os.path.exists(checkpoint_path):
        print(f"\n✓ Found checkpoint: {CHECKPOINT_FILE}")
        existing = pd.read_csv(checkpoint_path)
        print(f"  Records: {len(existing):,}")
        print(f"  Last date: {existing['GAME_DATE'].max()}")
        
        resume = input("\n  Resume from checkpoint? (y/n): ").strip().lower()
        if resume == 'y':
            all_stats.append(existing)
            collected_dates = set(existing['GAME_DATE'].unique())
            print(f"  ✓ Resuming with {len(collected_dates)} dates already collected\n")
        else:
            print("  Starting fresh collection...\n")
    
    # Get unique date-season combinations
    games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
    date_season_pairs = games_df[['GAME_DATE', 'SEASON']].drop_duplicates()
    date_season_pairs = date_season_pairs.sort_values('GAME_DATE')
    
    total_dates = len(date_season_pairs)
    print(f"Total dates to collect: {total_dates}")
    print(f"Estimated time: {total_dates * RATE_LIMIT_DELAY * 2 / 60:.1f} minutes")
    print(f"(Collecting Advanced + Four Factors for each date)")
    print(f"\n💡 OPTIMIZATION: Only collecting stats for teams that played on each date")
    print(f"   This reduces data volume by ~50% compared to collecting all 30 teams\n")
    
    failed_dates = []
    checkpoint_counter = len(collected_dates)
    
    for idx, (_, row) in enumerate(date_season_pairs.iterrows(), 1):
        date = row['GAME_DATE']
        season = row['SEASON']
        date_str = date.strftime('%Y-%m-%d')
        
        # Skip if already collected
        if date_str in collected_dates:
            print(f"[{idx}/{total_dates}] {season} {date_str} ... ⏭️  Already collected")
            continue
        
        # Get teams that played on this date
        teams_on_date = games_df[
            (games_df['GAME_DATE'] == date) & 
            (games_df['SEASON'] == season)
        ]
        
        # Extract unique team IDs (both home and away)
        home_teams = teams_on_date['HOME_TEAM_ID'].unique().tolist()
        away_teams = teams_on_date['AWAY_TEAM_ID'].unique().tolist()
        team_ids = list(set(home_teams + away_teams))
        
        team_count = len(team_ids)
        
        print(f"[{idx}/{total_dates}] {season} {date_str} ({team_count} teams) ...", end=" ")
        
        # Collect Advanced Stats (only for teams that played)
        adv_df, adv_error = fetch_stats_for_date(season, date_str, team_ids, 'Advanced')
        
        # Collect Four Factors (only for teams that played)
        ff_df, ff_error = fetch_stats_for_date(season, date_str, team_ids, 'Four Factors')
        
        # Check results
        if not adv_df.empty and not ff_df.empty:
            # Both successful - merge them
            merged = merge_advanced_and_four_factors(adv_df, ff_df)
            all_stats.append(merged)
            print(f"✓ {len(merged)} teams (Adv + FF)")
            
        elif not adv_df.empty:
            # Only Advanced successful
            all_stats.append(adv_df)
            print(f"⚠️  {len(adv_df)} teams (Adv only, FF failed)")
            failed_dates.append((season, date_str, f"FF: {ff_error}"))
            
        elif not ff_df.empty:
            # Only Four Factors successful
            all_stats.append(ff_df)
            print(f"⚠️  {len(ff_df)} teams (FF only, Adv failed)")
            failed_dates.append((season, date_str, f"Adv: {adv_error}"))
            
        else:
            # Both failed
            print(f"✗ Failed (both)")
            failed_dates.append((season, date_str, f"Both failed"))
        
        # Checkpoint saving
        checkpoint_counter += 1
        if checkpoint_counter % CHECKPOINT_INTERVAL == 0 and all_stats:
            temp_df = pd.concat(all_stats, ignore_index=True)
            temp_df.to_csv(checkpoint_path, index=False)
            print(f"    💾 Checkpoint saved: {len(temp_df):,} records")
    
    # Combine all
    if all_stats:
        combined = pd.concat(all_stats, ignore_index=True)
        return combined, failed_dates
    else:
        return pd.DataFrame(), failed_dates


# ============================================================
# MAIN
# ============================================================

def main():
    """Main execution workflow."""
    start_time = datetime.now()
    
    print("\n" + "="*70)
    print("ADVANCED STATS COLLECTION")
    print("="*70)
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Input: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    
    # Load game data
    print("\n[STEP 1] Loading game data...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"✗ Error: Input file not found!")
        print(f"  Expected: {INPUT_FILE}")
        print(f"\n  Run collect_nba_games_improved.py first!")
        return
    
    games_df = pd.read_csv(INPUT_FILE, parse_dates=['GAME_DATE'])
    print(f"✓ Loaded {len(games_df):,} games")
    
    # Filter seasons if specified
    if SEASONS_FILTER:
        print(f"\nFiltering to seasons: {', '.join(SEASONS_FILTER)}")
        games_df = games_df[games_df['SEASON'].isin(SEASONS_FILTER)]
        print(f"✓ Filtered to {len(games_df):,} games")
    
    seasons = sorted(games_df['SEASON'].unique())
    print(f"Seasons: {', '.join(seasons)}")
    print(f"Date range: {games_df['GAME_DATE'].min().date()} to {games_df['GAME_DATE'].max().date()}")
    
    # Collect stats
    print("\n[STEP 2] Collecting team statistics...")
    print("Will collect for each date:")
    print("  - Advanced Stats (OFF_RATING, DEF_RATING, NET_RATING, PACE, etc.)")
    print("  - Four Factors (EFG_PCT, TOV_PCT, OREB_PCT, FTA_RATE, etc.)")
    
    stats_df, failed = collect_stats_for_all_dates(games_df)
    
    if stats_df.empty:
        print("\n✗ No data collected!")
        return
    
    # Save final output
    print("\n[STEP 3] Saving final output...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    stats_df.to_csv(output_path, index=False)
    
    # Remove checkpoint file
    checkpoint_path = os.path.join(OUTPUT_DIR, CHECKPOINT_FILE)
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
        print("✓ Removed checkpoint file")
    
    # Summary
    print("\n" + "="*70)
    print("✓ COLLECTION COMPLETE")
    print("="*70)
    print(f"Output: {output_path}")
    print(f"Records: {len(stats_df):,}")
    print(f"Columns: {len(stats_df.columns)}")
    print(f"Unique dates: {stats_df['GAME_DATE'].nunique()}")
    print(f"Seasons: {', '.join(sorted(stats_df['SEASON'].unique()))}")
    print(f"Date range: {stats_df['GAME_DATE'].min()} to {stats_df['GAME_DATE'].max()}")
    
    if failed:
        print(f"\n⚠️  Failed: {len(failed)} dates")
        if len(failed) <= 10:
            for season, date, error in failed:
                print(f"  {season} {date}: {error[:50]}")
        else:
            print(f"  (Showing first 10)")
            for season, date, error in failed[:10]:
                print(f"  {season} {date}: {error[:50]}")
    
    # Check for key columns
    print("\n✓ Key columns present:")
    key_cols = [
        'TEAM_ID', 'TEAM_NAME', 'GP', 'W', 'L', 'W_PCT',
        'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE',
        'EFG_PCT', 'TM_TOV_PCT', 'OREB_PCT', 'FTA_RATE',
        'OPP_EFG_PCT', 'OPP_TOV_PCT', 'DREB_PCT', 'OPP_FTA_RATE'
    ]
    
    present = [col for col in key_cols if col in stats_df.columns]
    missing = [col for col in key_cols if col not in stats_df.columns]
    
    for col in present[:10]:
        print(f"  ✓ {col}")
    if len(present) > 10:
        print(f"  ... and {len(present) - 10} more")
    
    if missing:
        print(f"\n⚠️  Missing columns: {', '.join(missing)}")
    
    # Execution time
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n⏱️  Execution time: {duration}")
    
    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. ✓ You now have team stats by date")
    print("2. → Next: Merge stats with games to create _PRIOR columns")
    print("3. → Then: Run feature engineering")
    print("4. → Then: Filter early games")
    print("5. → Finally: Train model")
    print("="*70)


if __name__ == "__main__":
    main()