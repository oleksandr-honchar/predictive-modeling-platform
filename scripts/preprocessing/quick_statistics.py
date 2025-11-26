"""
NBA TRAINING DATA - LOADING AND STATISTICS (Windows Path Corrected)
====================================================================

Quick fix for Windows file paths.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CORRECT FILE PATH FOR YOUR SYSTEM
# ============================================================================

# Update this to match your actual file location
DATA_PATH = "C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\nba_train_data.csv"

# Alternative: Use forward slashes (works on Windows too)
# DATA_PATH = "C:/Users/userPC/projects/predictive-modeling-platform/data/processed/nba/nba_training_data.csv"

# Alternative: Use raw string (no need to escape backslashes)
# DATA_PATH = r"C:\Users\userPC\projects\predictive-modeling-platform\data\processed\nba\nba_training_data.csv"


# ============================================================================
# QUICK LOAD FUNCTION
# ============================================================================

def quick_load(csv_path=DATA_PATH):
    """Load data quickly with proper date handling."""
    print(f"Loading from: {csv_path}")
    df = pd.read_csv(csv_path)
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values('GAME_DATE').reset_index(drop=True)
    print(f"✅ Loaded {len(df):,} games")
    return df


# ============================================================================
# BASIC STATISTICS
# ============================================================================

def print_quick_stats(df):
    """Print essential statistics quickly."""
    print("\n" + "=" * 80)
    print("QUICK STATISTICS")
    print("=" * 80)
    
    # Basic info
    print(f"\nDataset Size:")
    print(f"  Total games:    {len(df):,}")
    print(f"  Total columns:  {len(df.columns)}")
    print(f"  Memory usage:   {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Date range
    print(f"\nDate Range:")
    print(f"  Start:  {df['GAME_DATE'].min().strftime('%Y-%m-%d')}")
    print(f"  End:    {df['GAME_DATE'].max().strftime('%Y-%m-%d')}")
    print(f"  Span:   {(df['GAME_DATE'].max() - df['GAME_DATE'].min()).days:,} days")
    
    # Seasons
    print(f"\nSeasons:")
    print(f"  Count:  {df['SEASON'].nunique()}")
    print(f"  List:   {', '.join(sorted(df['SEASON'].unique()))}")
    
    # Games per season
    print(f"\nGames per season:")
    for season, count in df.groupby('SEASON').size().items():
        print(f"  {season}: {count:,} games")
    
    # Target variable
    if 'HOME_WIN' in df.columns:
        home_win_rate = df['HOME_WIN'].mean()
        home_wins = df['HOME_WIN'].sum()
        away_wins = len(df) - home_wins
        
        print(f"\nTarget Variable (HOME_WIN):")
        print(f"  Home wins:  {home_wins:,} ({home_win_rate:.1%})")
        print(f"  Away wins:  {away_wins:,} ({(1-home_win_rate):.1%})")
        print(f"  Advantage:  {(home_win_rate - 0.5) * 100:+.1f} percentage points")
    
    # Data quality
    missing = df.isnull().sum().sum()
    duplicates = df['GAME_ID'].duplicated().sum() if 'GAME_ID' in df.columns else 0
    
    print(f"\nData Quality:")
    print(f"  Missing values:  {missing} {'✅' if missing == 0 else '⚠️'}")
    print(f"  Duplicate games: {duplicates} {'✅' if duplicates == 0 else '⚠️'}")
    print(f"  Sorted by date:  {'✅' if df['GAME_DATE'].is_monotonic_increasing else '❌'}")
    
    # Feature types
    all_cols = df.columns.tolist()
    prior_features = [col for col in all_cols if '_PRIOR' in col]
    diff_features = [col for col in all_cols if '_DIFF' in col]
    rest_features = [col for col in all_cols if 'REST' in col or 'B2B' in col]
    
    print(f"\nFeature Types:")
    print(f"  _PRIOR features: {len(prior_features)}")
    print(f"  _DIFF features:  {len(diff_features)}")
    print(f"  REST features:   {len(rest_features)}")
    print(f"  Total predictive: {len(prior_features) + len(diff_features) + len(rest_features)}")
    
    print("\n" + "=" * 80)


def analyze_key_features(df):
    """Analyze the most important features."""
    print("\n" + "=" * 80)
    print("KEY FEATURES ANALYSIS")
    print("=" * 80)
    
    key_features = {
        'NET_RATING_DIFF': 'Net Rating Differential',
        'WIN_PCT_DIFF': 'Win% Differential',
        'EFG_PCT_DIFF': 'eFG% Differential',
        'TOV_PCT_DIFF': 'Turnover% Differential',
        'OREB_PCT_DIFF': 'ORB% Differential',
        'FTA_RATE_DIFF': 'FTA Rate Differential',
        'REST_ADVANTAGE': 'Rest Advantage'
    }
    
    for feature, description in key_features.items():
        if feature in df.columns:
            mean = df[feature].mean()
            std = df[feature].std()
            min_val = df[feature].min()
            max_val = df[feature].max()
            
            print(f"\n{description} ({feature}):")
            print(f"  Mean:  {mean:7.3f}")
            print(f"  Std:   {std:7.3f}")
            print(f"  Range: [{min_val:7.3f}, {max_val:7.3f}]")
            
            # Correlation with target
            if 'HOME_WIN' in df.columns:
                corr = df[feature].corr(df['HOME_WIN'])
                print(f"  Correlation with HOME_WIN: {corr:+.3f}")
                
                if abs(corr) > 0.3:
                    print(f"    → {'Strong' if abs(corr) > 0.5 else 'Moderate'} predictor! ✅")


def plot_target_distribution(df, save_path=None):
    """Plot HOME_WIN distribution."""
    if 'HOME_WIN' not in df.columns:
        print("⚠️  HOME_WIN column not found")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    home_wins = df['HOME_WIN'].sum()
    away_wins = len(df) - home_wins
    home_win_rate = df['HOME_WIN'].mean()
    
    bars = ax.bar(['Home Win', 'Away Win'], [home_wins, away_wins], 
                  color=['#1f77b4', '#ff7f0e'], edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Number of Games', fontsize=12)
    ax.set_title('Game Outcomes Distribution', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for i, (count, label) in enumerate([(home_wins, 'Home'), (away_wins, 'Away')]):
        pct = count / len(df) * 100
        ax.text(i, count, f'{count:,}\n({pct:.1f}%)', 
               ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Plot saved to {save_path}")
    
    plt.show()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "NBA TRAINING DATA - STATISTICS" + " " * 27 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # Load data
        df = quick_load(DATA_PATH)
        
        # Print statistics
        print_quick_stats(df)
        
        # Analyze key features
        analyze_key_features(df)
        
        # Plot target distribution
        print("\n" + "=" * 80)
        print("GENERATING VISUALIZATION")
        print("=" * 80)
        plot_target_distribution(df, save_path='target_distribution.png')
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 80)
        
        print("\nDataFrame loaded as 'df'")
        print("You can now use it for further analysis:")
        print("  - df.head() to view first rows")
        print("  - df.describe() for statistics")
        print("  - df.columns to see all columns")
        
    except FileNotFoundError:
        print("\n" + "=" * 80)
        print("❌ FILE NOT FOUND")
        print("=" * 80)
        print(f"\nCould not find file at: {DATA_PATH}")
        print("\nPlease check:")
        print("  1. File path is correct")
        print("  2. File exists at that location")
        print("  3. You have permission to read the file")
        print("\nCurrent path in script:")
        print(f"  {DATA_PATH}")
        print("\nTo fix, update DATA_PATH at the top of this script")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()