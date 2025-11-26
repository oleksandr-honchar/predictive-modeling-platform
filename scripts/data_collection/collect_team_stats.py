"""
Collect advanced team statistics (ORtg, DRtg, Four Factors)
Created: 2025-11-24

USAGE:
    python collect_team_stats.py

OUTPUT:
    data/raw/nba/nba_team_advanced_stats.csv

STATISTICS COLLECTED:
    - Offensive Rating (ORtg)
    - Defensive Rating (DRtg)
    - Four Factors: eFG%, TOV%, ORB%, FT/FGA
    - Net Rating (NetRtg)
    - Pace
"""

from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.static import teams
import pandas as pd
import time
from datetime import datetime
import os

# ============================================================
# CONFIGURATION
# ============================================================

SEASONS = ['2021-22', '2022-23', '2023-24', '2024-25', '2025-26']
OUTPUT_DIR = 'data/raw/nba'
OUTPUT_FILE = 'nba_team_advanced_stats.csv'
RATE_LIMIT_DELAY = 0.6  # seconds between API calls

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def collect_advanced_stats_for_season(season):
    """
    Collect advanced team statistics for a specific season
    
    Args:
        season (str): Season string (e.g., '2023-24')
    
    Returns:
        pd.DataFrame: Advanced stats for all teams in the season
    """
    print(f"\n{'='*60}")
    print(f"Collecting advanced stats for {season} season...")
    print(f"{'='*60}")
    
    try:
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        # Fetch advanced stats
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season=season,
            season_type_all_star='Regular Season',
            measure_type_detailed_defense='Advanced'
        )
        
        stats_df = stats.get_data_frames()[0]
        
        # Add season identifier
        stats_df['SEASON'] = season
        
        print(f"✅ Collected stats for {len(stats_df)} teams")
        print(f"Columns: {list(stats_df.columns)}")
        
        return stats_df
        
    except Exception as e:
        print(f"❌ Error fetching stats for {season}: {e}")
        return pd.DataFrame()

def collect_four_factors_for_season(season):
    """
    Collect Four Factors for a specific season
    
    Args:
        season (str): Season string (e.g., '2023-24')
    
    Returns:
        pd.DataFrame: Four Factors for all teams in the season
    """
    print(f"\nCollecting Four Factors for {season}...")
    
    try:
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        # Fetch Four Factors
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season=season,
            season_type_all_star='Regular Season',
            measure_type_detailed_defense='Four Factors'
        )
        
        four_factors_df = stats.get_data_frames()[0]
        
        # Add season identifier
        four_factors_df['SEASON'] = season
        
        print(f"✅ Four Factors collected for {len(four_factors_df)} teams")
        
        return four_factors_df
        
    except Exception as e:
        print(f"❌ Error fetching Four Factors for {season}: {e}")
        return pd.DataFrame()

def merge_stats_and_factors(advanced_stats, four_factors):
    """
    Merge advanced stats and four factors DataFrames
    
    Args:
        advanced_stats (pd.DataFrame): Advanced statistics
        four_factors (pd.DataFrame): Four Factors statistics
    
    Returns:
        pd.DataFrame: Merged dataset
    """
    # Key columns to keep from each dataset
    advanced_cols = ['TEAM_ID', 'TEAM_NAME', 'SEASON', 'OFF_RATING', 'DEF_RATING', 
                     'NET_RATING', 'PACE', 'W', 'L', 'W_PCT']
    
    four_factors_cols = ['TEAM_ID', 'SEASON', 'EFG_PCT', 'FTA_RATE', 'TM_TOV_PCT', 
                         'OREB_PCT', 'OPP_EFG_PCT', 'OPP_FTA_RATE', 
                         'OPP_TOV_PCT', 'OPP_OREB_PCT']
    
    # Select columns (only those that exist)
    advanced_subset = advanced_stats[[col for col in advanced_cols if col in advanced_stats.columns]]
    four_factors_subset = four_factors[[col for col in four_factors_cols if col in four_factors.columns]]
    
    # Merge on TEAM_ID and SEASON
    merged_df = pd.merge(
        advanced_subset,
        four_factors_subset,
        on=['TEAM_ID', 'SEASON'],
        how='inner'
    )
    
    return merged_df

def save_data(df, output_path):
    """
    Save DataFrame to CSV with metadata
    
    Args:
        df (pd.DataFrame): Data to save
        output_path (str): Full path to output file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\n{'='*60}")
    print(f"✅ Data saved successfully!")
    print(f"📁 Location: {output_path}")
    print(f"📊 Total records: {len(df):,}")
    print(f"📅 Seasons: {df['SEASON'].unique().tolist()}")
    print(f"🏀 Teams per season: {len(df) // len(df['SEASON'].unique())}")
    print(f"{'='*60}")

# ============================================================
# MAIN COLLECTION PROCESS
# ============================================================

def main():
    """
    Main data collection workflow for advanced statistics
    """
    start_time = datetime.now()
    print("\n" + "="*60)
    print("NBA ADVANCED TEAM STATISTICS COLLECTION")
    print("="*60)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Seasons to collect: {', '.join(SEASONS)}")
    
    all_advanced_stats = []
    all_four_factors = []
    
    # Step 1: Collect data for each season
    for season in SEASONS:
        # Collect advanced stats
        advanced_df = collect_advanced_stats_for_season(season)
        if not advanced_df.empty:
            all_advanced_stats.append(advanced_df)
        
        # Collect Four Factors
        four_factors_df = collect_four_factors_for_season(season)
        if not four_factors_df.empty:
            all_four_factors.append(four_factors_df)
    
    # Step 2: Combine all seasons
    print("\n[STEP 2] Combining all seasons...")
    
    if all_advanced_stats and all_four_factors:
        combined_advanced = pd.concat(all_advanced_stats, ignore_index=True)
        combined_four_factors = pd.concat(all_four_factors, ignore_index=True)
        
        print(f"✅ Advanced stats: {len(combined_advanced):,} records")
        print(f"✅ Four Factors: {len(combined_four_factors):,} records")
        
        # Step 3: Merge datasets
        print("\n[STEP 3] Merging datasets...")
        final_df = merge_stats_and_factors(combined_advanced, combined_four_factors)
        print(f"✅ Merged dataset: {len(final_df):,} records")
        
        # Step 4: Data quality checks
        print("\n[STEP 4] Running data quality checks...")
        print(f"Columns: {list(final_df.columns)}")
        print(f"\nMissing values:\n{final_df.isnull().sum()[final_df.isnull().sum() > 0]}")
        print(f"\nSample statistics:")
        print(final_df[['TEAM_NAME', 'SEASON', 'OFF_RATING', 'DEF_RATING', 'NET_RATING']].head(10))
        
        # Step 5: Save data
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        save_data(final_df, output_path)
        
    else:
        print("❌ No data collected")
        return
    
    # Completion stats
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n⏱️  Total execution time: {duration}")
    print(f"✅ Collection complete!")

if __name__ == "__main__":
    main()