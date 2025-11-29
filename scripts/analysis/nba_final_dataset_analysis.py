"""
NBA FINAL DATASET ANALYSIS - LOWERCASE COLUMN NAMES
===================================================

Feature groups and analysis using lowercase column names.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# FILE PATH
# ============================================================================
DATA_PATH = r"C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\final\\nba_train_data.csv"

# ============================================================================
# FEATURE GROUPS (EXACT NAMES - LOWERCASE)
# ============================================================================
FEATURES_BASELINE = ["net_rating_diff"]

FEATURES_FOUR_FACTORS = [
    "efg_pct_diff", "tov_pct_diff", "oreb_pct_diff", "fta_rate_diff"
]

FEATURES_ROLLING = [
    "net_rating_l5_diff", "net_rating_l10_diff",
    "w_pct_l5_diff", "efg_pct_diff"
]

FEATURES_MOMENTUM = ["momentum_diff", "win_streak_diff"]

FEATURES_REST = [
    "rest_advantage",
    "home_b2b", "away_b2b",
    "b2b_in_l5_diff", "b2b_in_l10_diff",
    "avg_rest_l10_diff",
    "optimal_rest_diff",
    "over_rested_diff"
]

FEATURES_H2H = [
    "h2h_home_win_pct", "h2h_home_wins", "h2h_games"
]

FEATURES_ENGINEERED = (
    FEATURES_FOUR_FACTORS +
    FEATURES_ROLLING +
    FEATURES_MOMENTUM +
    FEATURES_REST +
    FEATURES_H2H
)

FEATURE_SETS = {
    "Baseline": FEATURES_BASELINE,
    "Four Factors": FEATURES_FOUR_FACTORS,
    "Rolling Performance": FEATURES_ROLLING,
    "Momentum": FEATURES_MOMENTUM,
    "Rest & Fatigue": FEATURES_REST,
    "Head-to-Head": FEATURES_H2H,
    "Engineered SuperSet": FEATURES_ENGINEERED
}

# ============================================================================
# LOAD DATA
# ============================================================================
def quick_load(csv_path=DATA_PATH):
    print(f"Loading from: {csv_path}")
    df = pd.read_csv(csv_path)
    df['game_date'] = pd.to_datetime(df['game_date'])
    df = df.sort_values('game_date').reset_index(drop=True)
    print(f"✅ Loaded {len(df):,} games with {len(df.columns)} columns")
    return df

# ============================================================================
# QUICK DATA SUMMARY
# ============================================================================
def print_quick_stats(df):
    print("\n" + "=" * 80)
    print("QUICK STATISTICS")
    print("=" * 80)
    
    print(f"\nDataset Size: {len(df):,} games, {len(df.columns)} columns")
    print(f"Memory Usage: {df.memory_usage(deep=True).sum()/1024**2:.2f} MB")
    
    print(f"\nDate Range: {df['game_date'].min().strftime('%Y-%m-%d')} to {df['game_date'].max().strftime('%Y-%m-%d')}")
    
    if 'season' in df.columns:
        print(f"\nSeasons ({df['season'].nunique()}): {', '.join(sorted(df['season'].unique()))}")
        print("Games per season:")
        for season, count in df.groupby('season').size().sort_index().items():
            print(f"  {season}: {count:,} games")
    
    if 'home_win' in df.columns:
        home_win_rate = df['home_win'].mean()
        print(f"\nhome_win: {df['home_win'].sum():,} home wins ({home_win_rate:.1%})")
    
    missing = df.isnull().sum().sum()
    duplicates = df['game_id'].duplicated().sum() if 'game_id' in df.columns else 0
    print(f"\nData Quality: Missing={missing}, Duplicates={duplicates}")

# ============================================================================
# FEATURE SET ANALYSIS
# ============================================================================
def analyze_feature_set(df, feature_set_name, features):
    print("\n" + "=" * 80)
    print(f"FEATURE SET ANALYSIS: {feature_set_name}")
    print("=" * 80)
    
    for f in features:
        if f in df.columns:
            mean = df[f].mean()
            std = df[f].std()
            min_val = df[f].min()
            max_val = df[f].max()
            corr = df[f].corr(df['home_win']) if 'home_win' in df.columns else np.nan
            print(f"{f:30} | Mean: {mean:+.3f}, Std: {std:.3f}, Range: [{min_val:+.3f}, {max_val:+.3f}], Corr(home_win): {corr:+.3f}")
        else:
            print(f"{f:30} | ⚠️ Missing in dataset")

# ============================================================================
# FOUR FACTORS ANALYSIS
# ============================================================================
def analyze_four_factors(df):
    print("\n" + "=" * 80)
    print("FOUR FACTORS ANALYSIS")
    print("=" * 80)
    
    ff_features = ["efg_pct_diff", "tov_pct_diff", "oreb_pct_diff", "fta_rate_diff"]
    for f in ff_features:
        if f in df.columns:
            corr = df[f].corr(df['home_win'])
            mean = df[f].mean()
            std = df[f].std()
            print(f"{f:30} | Corr: {corr:+.3f}, Mean: {mean:+.3f}, Std: {std:.3f}")
        else:
            print(f"{f:30} | ⚠️ Missing in dataset")

# ============================================================================
# TARGET DISTRIBUTION
# ============================================================================
def plot_target_distribution(df, save_path=None):
    if 'home_win' not in df.columns:
        print("⚠️ home_win column not found")
        return
    
    fig, ax = plt.subplots(figsize=(10,6))
    home_wins = int(df['home_win'].sum())
    away_wins = len(df)-home_wins
    bars = ax.bar(['Home Win', 'Away Win'], [home_wins, away_wins], color=['#1f77b4','#ff7f0e'], edgecolor='black')
    
    for i, count in enumerate([home_wins, away_wins]):
        pct = count / len(df) * 100
        ax.text(i, count, f'{count:,}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=12)
    
    ax.set_ylabel("Number of Games")
    ax.set_title("Game Outcome Distribution")
    ax.axhline(len(df)/2, color='red', linestyle='--', alpha=0.5, label="50-50 baseline")
    ax.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================
def plot_correlation_heatmap(df, feature_list, save_path=None):
    """Plot correlation heatmap for specified features."""
    if 'home_win' not in df.columns:
        print("⚠️ home_win column not found")
        return
    
    # Get features that exist in dataframe
    available_features = [f for f in feature_list if f in df.columns]
    
    if not available_features:
        print("⚠️ No features found in dataframe")
        return
    
    # Create correlation matrix
    features_with_target = available_features + ['home_win']
    corr_matrix = df[features_with_target].corr()
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Matrix", fontsize=14, pad=20)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================================
# TARGET VARIABLE DISTRIBUTIONS
# ============================================================================
def plot_all_targets(df, save_path=None):
    """Plot distributions of all target variables."""
    targets = ['home_win', 'spread', 'total']
    available_targets = [t for t in targets if t in df.columns]
    
    if not available_targets:
        print("⚠️ No target variables found")
        return
    
    n_targets = len(available_targets)
    fig, axes = plt.subplots(1, n_targets, figsize=(6*n_targets, 5))
    
    if n_targets == 1:
        axes = [axes]
    
    for ax, target in zip(axes, available_targets):
        if target == 'home_win':
            # Binary target - bar chart
            counts = df[target].value_counts()
            ax.bar(['Away Win', 'Home Win'], [counts.get(0, 0), counts.get(1, 0)],
                   color=['#ff7f0e', '#1f77b4'], edgecolor='black')
            ax.set_ylabel('Count')
            ax.set_title(f'{target.replace("_", " ").title()}\n({df[target].mean():.1%} home wins)')
        else:
            # Continuous target - histogram
            ax.hist(df[target], bins=50, color='#2ca02c', alpha=0.7, edgecolor='black')
            ax.axvline(df[target].mean(), color='red', linestyle='--', 
                      label=f'Mean: {df[target].mean():.1f}')
            ax.axvline(df[target].median(), color='orange', linestyle='--',
                      label=f'Median: {df[target].median():.1f}')
            ax.set_xlabel(target.replace('_', ' ').title())
            ax.set_ylabel('Frequency')
            ax.set_title(f'{target.replace("_", " ").title()} Distribution')
            ax.legend()
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    df = quick_load(DATA_PATH)
    print_quick_stats(df)
    
    # Analyze each feature set
    for set_name, features in FEATURE_SETS.items():
        analyze_feature_set(df, set_name, features)
    
    # Four Factors analysis
    analyze_four_factors(df)
    
    # Plot distributions
    print("\n" + "=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    
    plot_target_distribution(df, save_path='target_distribution.png')
    plot_all_targets(df, save_path='all_targets_distribution.png')
    plot_correlation_heatmap(df, FEATURES_ENGINEERED, save_path='feature_correlation.png')
    
    print("\n✅ ANALYSIS COMPLETE! DataFrame loaded as 'df'.")