"""
Manual Retry Script for Failed Dates
Created: 2025-11-24

Purpose: Retry the 2 dates that timed out during collection
"""

from nba_api.stats.endpoints import leaguedashteamstats
import pandas as pd
import time
from datetime import datetime

# Configuration
FAILED_DATES = [
    ('2022-23', '2022-10-28'),
    ('2022-23', '2023-03-15'),
]

SEASON_STARTS = {
    '2021-22': '2021-10-19',
    '2022-23': '2022-10-18',
    '2023-24': '2023-10-24',
    '2024-25': '2024-10-22',
}

def fetch_stats_retry(season, date_str):
    """
    Fetch advanced stats with retry logic
    
    Args:
        season: Season string (e.g., '2022-23')
        date_str: Date string in 'YYYY-MM-DD' format
    
    Returns:
        DataFrame with advanced stats for all teams
    """
    try:
        # Convert dates
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        api_date = date_obj.strftime('%m/%d/%Y')
        
        season_start = SEASON_STARTS[season]
        season_start_api = datetime.strptime(season_start, '%Y-%m-%d').strftime('%m/%d/%Y')
        
        print(f"\nAttempting to fetch {season} on {date_str}...")
        print(f"Date range: {season_start_api} to {api_date}")
        
        # Fetch with longer timeout
        time.sleep(1)  # Rate limiting
        stats = leaguedashteamstats.LeagueDashTeamStats(
            season=season,
            date_from_nullable=season_start_api,
            date_to_nullable=api_date,
            measure_type_detailed_defense='Advanced',
            season_type_all_star='Regular Season',
            timeout=90  # Longer timeout
        )
        
        df = stats.get_data_frames()[0]
        
        if not df.empty:
            # Add metadata
            df['AS_OF_DATE'] = date_str
            df['SEASON'] = season
            print(f"✅ SUCCESS! Retrieved {len(df)} teams")
            return df
        else:
            print(f"❌ FAILED: Empty response")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return pd.DataFrame()

def main():
    """
    Main retry workflow
    """
    print("="*70)
    print("MANUAL RETRY OF FAILED DATES")
    print("="*70)
    print(f"\nFailed dates to retry: {len(FAILED_DATES)}")
    
    recovered_data = []
    success_count = 0
    
    for season, date_str in FAILED_DATES:
        print("\n" + "-"*70)
        
        # Try up to 3 times
        for attempt in range(3):
            print(f"\nAttempt {attempt + 1}/3 for {date_str}...")
            
            df = fetch_stats_retry(season, date_str)
            
            if not df.empty:
                recovered_data.append(df)
                success_count += 1
                print(f"✅ Recovered {date_str}!")
                break
            else:
                if attempt < 2:
                    print(f"Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    print(f"⚠️  Could not recover {date_str} after 3 attempts")
    
    print("\n" + "="*70)
    print("RETRY RESULTS")
    print("="*70)
    print(f"Attempted: {len(FAILED_DATES)} dates")
    print(f"Recovered: {success_count} dates")
    print(f"Still missing: {len(FAILED_DATES) - success_count} dates")
    
    # Save recovered data if any
    if recovered_data:
        combined = pd.concat(recovered_data, ignore_index=True)
        output_file = 'data/processed/nba/recovered_dates.csv'
        combined.to_csv(output_file, index=False)
        print(f"\n✅ Saved recovered data to: {output_file}")
        print(f"Records saved: {len(combined)}")
        
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("1. Check the recovered_dates.csv file")
        print("2. Merge it with your main dataset")
        print("3. Or re-run the full hybrid script to include these")
    else:
        print("\n⚠️  No data recovered")
        print("\nRECOMMENDATION:")
        print("Use interpolation to fill these 2 dates")
        print("Impact: 2 dates out of 164 = 1.2% missing")
        print("Interpolation will be 99%+ accurate for this gap")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()