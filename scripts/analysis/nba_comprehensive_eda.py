"""
NBA COMPREHENSIVE EDA - UPDATED FOR NEW DATASET
================================================

Comprehensive exploratory data analysis for the enhanced NBA dataset with:
- Lowercase column names
- 262 features including rolling windows (L5, L10)
- Rest and fatigue features
- Momentum indicators
- Head-to-head statistics
- 5,085 games (after filtering first game of season)
- Target variables: home_win, home_pts, away_pts, spread, total

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_PATH = "C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\final\\nba_train_data.csv"
OUTPUT_DIR = "eda_outputs/"

# Feature groups for analysis
FEATURE_GROUPS = {
    "Baseline": ["net_rating_diff"],
    
    "Four Factors": [
        "efg_pct_diff", "tov_pct_diff", "oreb_pct_diff", "fta_rate_diff"
    ],
    
    "Rolling Performance (L5)": [
        "net_rating_l5_diff", "w_pct_l5_diff", 
        "efg_pct_l5_diff", "tov_pct_l5_diff"
    ],
    
    "Rolling Performance (L10)": [
        "net_rating_l10_diff", "w_pct_l10_diff",
        "efg_pct_l10_diff", "tov_pct_l10_diff"
    ],
    
    "Momentum": ["momentum_diff", "win_streak_diff"],
    
    "Rest & Fatigue": [
        "rest_advantage", "b2b_diff",
        "home_b2b", "away_b2b",
        "b2b_in_l5_diff", "b2b_in_l10_diff",
        "avg_rest_l10_diff", "optimal_rest_diff", "over_rested_diff"
    ],
    
    "Head-to-Head": [
        "h2h_home_win_pct", "h2h_home_wins", "h2h_games"
    ]
}

TARGET_VARS = ["home_win", "home_pts", "away_pts", "spread", "total"]

# ============================================================================
# 1. LOAD AND BASIC INSPECTION
# ============================================================================

def load_and_inspect(filepath):
    """Load data and perform basic inspection."""
    print("="*80)
    print("LOADING DATASET")
    print("="*80)
    
    df = pd.read_csv(filepath)
    
    # Convert date column
    df['game_date'] = pd.to_datetime(df['game_date'])
    df = df.sort_values('game_date').reset_index(drop=True)
    
    print(f"\n✓ Loaded dataset: {filepath}")
    print(f"  Shape: {df.shape[0]:,} games × {df.shape[1]} features")
    print(f"  Date range: {df['game_date'].min().date()} to {df['game_date'].max().date()}")
    print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Season breakdown
    if 'season' in df.columns:
        print(f"\n  Seasons: {df['season'].nunique()}")
        for season in sorted(df['season'].unique()):
            count = len(df[df['season'] == season])
            print(f"    {season}: {count:,} games")
    
    return df

# ============================================================================
# 2. DATA QUALITY ASSESSMENT
# ============================================================================

def assess_data_quality(df):
    """Comprehensive data quality check."""
    print("\n" + "="*80)
    print("DATA QUALITY ASSESSMENT")
    print("="*80)
    
    # Missing values
    missing = df.isnull().sum()
    total_missing = missing.sum()
    
    if total_missing > 0:
        print(f"\n⚠ Missing Values: {total_missing:,} ({total_missing/(df.shape[0]*df.shape[1])*100:.3f}%)")
        print("\nColumns with missing values:")
        for col in missing[missing > 0].index:
            pct = missing[col] / len(df) * 100
            print(f"  {col:40} {missing[col]:5,} ({pct:5.2f}%)")
    else:
        print("\n✓ No missing values detected")
    
    # Duplicates
    if 'game_id' in df.columns:
        dupes = df['game_id'].duplicated().sum()
        print(f"\n✓ Duplicate game_ids: {dupes}")
    
    # Target variable check
    if 'home_win' in df.columns:
        home_wins = df['home_win'].sum()
        home_win_pct = home_wins / len(df) * 100
        print(f"\n✓ Target Distribution:")
        print(f"    Home wins: {int(home_wins):,} ({home_win_pct:.2f}%)")
        print(f"    Away wins: {len(df) - int(home_wins):,} ({100-home_win_pct:.2f}%)")
    
    # New target variables
    if 'spread' in df.columns:
        print(f"\n✓ Spread Statistics:")
        print(f"    Mean: {df['spread'].mean():+.2f} points (home advantage)")
        print(f"    Median: {df['spread'].median():+.2f} points")
        print(f"    Std: {df['spread'].std():.2f} points")
    
    if 'total' in df.columns:
        print(f"\n✓ Total Points Statistics:")
        print(f"    Mean: {df['total'].mean():.1f} points")
        print(f"    Median: {df['total'].median():.1f} points")
        print(f"    Std: {df['total'].std():.2f} points")
    
    return df

# ============================================================================
# 3. FEATURE CORRELATION ANALYSIS
# ============================================================================

def analyze_correlations(df, save_plots=True):
    """Analyze feature correlations with target variable."""
    print("\n" + "="*80)
    print("FEATURE CORRELATION ANALYSIS")
    print("="*80)
    
    if 'home_win' not in df.columns:
        print("⚠ home_win column not found")
        return None
    
    # Get all numeric columns except targets
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    feature_cols = [col for col in numeric_cols if col not in TARGET_VARS]
    
    # Calculate correlations
    correlations = df[feature_cols].corrwith(df['home_win']).sort_values(ascending=False)
    
    # Display top/bottom features
    print("\nTop 20 Positive Correlations:")
    print("-" * 60)
    for i, (feat, corr) in enumerate(correlations.head(20).items(), 1):
        print(f"{i:2}. {feat:40} {corr:+.4f}")
    
    print("\nTop 20 Negative Correlations:")
    print("-" * 60)
    for i, (feat, corr) in enumerate(correlations.tail(20).items(), 1):
        print(f"{i:2}. {feat:40} {corr:+.4f}")
    
    # Analyze feature groups
    print("\n" + "="*80)
    print("FEATURE GROUP CORRELATIONS")
    print("="*80)
    
    for group_name, features in FEATURE_GROUPS.items():
        print(f"\n{group_name}:")
        print("-" * 60)
        for feat in features:
            if feat in df.columns:
                corr = df[feat].corr(df['home_win'])
                mean = df[feat].mean()
                std = df[feat].std()
                print(f"  {feat:35} r={corr:+.4f}  μ={mean:+.3f}  σ={std:.3f}")
            else:
                print(f"  {feat:35} ⚠ Not found in dataset")
    
    if save_plots:
        plot_correlation_analysis(df, correlations)
    
    return correlations

# ============================================================================
# 4. FOUR FACTORS DEEP DIVE
# ============================================================================

def analyze_four_factors(df, save_plots=True):
    """Detailed analysis of Dean Oliver's Four Factors."""
    print("\n" + "="*80)
    print("FOUR FACTORS ANALYSIS")
    print("="*80)
    
    four_factors = ["efg_pct_diff", "tov_pct_diff", "oreb_pct_diff", "fta_rate_diff"]
    
    results = []
    for factor in four_factors:
        if factor not in df.columns:
            print(f"⚠ {factor} not found")
            continue
        
        # Overall correlation
        corr = df[factor].corr(df['home_win'])
        
        # Split by outcome
        home_wins = df[df['home_win'] == 1][factor]
        home_losses = df[df['home_win'] == 0][factor]
        
        # Statistical test
        t_stat, p_value = stats.ttest_ind(home_wins, home_losses)
        
        results.append({
            'Factor': factor,
            'Correlation': corr,
            'Win Mean': home_wins.mean(),
            'Loss Mean': home_losses.mean(),
            'Difference': home_wins.mean() - home_losses.mean(),
            't-stat': t_stat,
            'p-value': p_value
        })
        
        print(f"\n{factor}:")
        print(f"  Correlation: {corr:+.4f}")
        print(f"  Home Wins:   μ={home_wins.mean():+.4f}, σ={home_wins.std():.4f}")
        print(f"  Home Losses: μ={home_losses.mean():+.4f}, σ={home_losses.std():.4f}")
        print(f"  Difference:  {home_wins.mean() - home_losses.mean():+.4f}")
        print(f"  t-statistic: {t_stat:+.3f}, p-value: {p_value:.6f}")
        if p_value < 0.001:
            print(f"  *** Highly significant")
        elif p_value < 0.01:
            print(f"  ** Significant")
        elif p_value < 0.05:
            print(f"  * Marginally significant")
    
    if save_plots and results:
        plot_four_factors(df, four_factors)
    
    return pd.DataFrame(results)

# ============================================================================
# 5. ROLLING WINDOW ANALYSIS
# ============================================================================

def analyze_rolling_features(df):
    """Compare L5 vs L10 rolling window features."""
    print("\n" + "="*80)
    print("ROLLING WINDOW ANALYSIS (L5 vs L10)")
    print("="*80)
    
    # Compare L5 and L10 for key metrics
    metrics = ['net_rating', 'w_pct', 'efg_pct', 'tov_pct']
    
    print("\nCorrelation Comparison (with home_win):")
    print("-" * 80)
    print(f"{'Metric':<20} {'L5 Corr':>12} {'L10 Corr':>12} {'Difference':>12} {'Winner':>10}")
    print("-" * 80)
    
    for metric in metrics:
        l5_col = f"{metric}_l5_diff"
        l10_col = f"{metric}_l10_diff"
        
        if l5_col in df.columns and l10_col in df.columns:
            l5_corr = df[l5_col].corr(df['home_win'])
            l10_corr = df[l10_col].corr(df['home_win'])
            diff = l5_corr - l10_corr
            winner = 'L5' if abs(l5_corr) > abs(l10_corr) else 'L10'
            
            print(f"{metric:<20} {l5_corr:+12.4f} {l10_corr:+12.4f} {diff:+12.4f} {winner:>10}")

# ============================================================================
# 6. REST AND FATIGUE ANALYSIS
# ============================================================================

def analyze_rest_features(df, save_plots=True):
    """Analyze impact of rest and back-to-back games."""
    print("\n" + "="*80)
    print("REST AND FATIGUE ANALYSIS")
    print("="*80)
    
    # Rest advantage
    if 'rest_advantage' in df.columns:
        corr = df['rest_advantage'].corr(df['home_win'])
        print(f"\nRest Advantage:")
        print(f"  Correlation: {corr:+.4f}")
        print(f"  Mean: {df['rest_advantage'].mean():+.2f} days")
        print(f"  Std: {df['rest_advantage'].std():.2f} days")
    
    # Back-to-back impact
    if 'home_b2b' in df.columns and 'away_b2b' in df.columns:
        print(f"\nBack-to-Back Games:")
        
        # When home team is B2B
        home_b2b_games = df[df['home_b2b'] == 1]
        if len(home_b2b_games) > 0:
            home_b2b_win_rate = home_b2b_games['home_win'].mean()
            print(f"  Home B2B games: {len(home_b2b_games):,} ({home_b2b_win_rate:.2%} win rate)")
        
        # When away team is B2B
        away_b2b_games = df[df['away_b2b'] == 1]
        if len(away_b2b_games) > 0:
            away_b2b_win_rate = away_b2b_games['home_win'].mean()
            print(f"  Away B2B games: {len(away_b2b_games):,} ({away_b2b_win_rate:.2%} home win rate)")
        
        # Both B2B
        both_b2b = df[(df['home_b2b'] == 1) & (df['away_b2b'] == 1)]
        if len(both_b2b) > 0:
            print(f"  Both B2B: {len(both_b2b):,} games ({both_b2b['home_win'].mean():.2%} home win rate)")
        
        # Neither B2B
        neither_b2b = df[(df['home_b2b'] == 0) & (df['away_b2b'] == 0)]
        if len(neither_b2b) > 0:
            print(f"  Neither B2B: {len(neither_b2b):,} games ({neither_b2b['home_win'].mean():.2%} home win rate)")
    
    if save_plots:
        plot_rest_analysis(df)

# ============================================================================
# 7. MOMENTUM ANALYSIS
# ============================================================================

def analyze_momentum(df):
    """Analyze momentum indicators."""
    print("\n" + "="*80)
    print("MOMENTUM ANALYSIS")
    print("="*80)
    
    if 'momentum_diff' in df.columns:
        corr = df['momentum_diff'].corr(df['home_win'])
        print(f"\nMomentum Differential:")
        print(f"  Correlation: {corr:+.4f}")
        print(f"  Mean: {df['momentum_diff'].mean():+.4f}")
        print(f"  Std: {df['momentum_diff'].std():.4f}")
    
    if 'win_streak_diff' in df.columns:
        corr = df['win_streak_diff'].corr(df['home_win'])
        print(f"\nWin Streak Differential:")
        print(f"  Correlation: {corr:+.4f}")
        print(f"  Mean: {df['win_streak_diff'].mean():+.2f}")
        print(f"  Max: {df['win_streak_diff'].max():.0f}")
        print(f"  Min: {df['win_streak_diff'].min():.0f}")

# ============================================================================
# 8. HEAD-TO-HEAD ANALYSIS
# ============================================================================

def analyze_h2h(df):
    """Analyze head-to-head statistics."""
    print("\n" + "="*80)
    print("HEAD-TO-HEAD ANALYSIS")
    print("="*80)
    
    if 'h2h_home_win_pct' in df.columns:
        corr = df['h2h_home_win_pct'].corr(df['home_win'])
        print(f"\nH2H Home Win Percentage:")
        print(f"  Correlation: {corr:+.4f}")
        print(f"  Mean: {df['h2h_home_win_pct'].mean():.3f}")
        print(f"  Median: {df['h2h_home_win_pct'].median():.3f}")
    
    if 'h2h_games' in df.columns:
        print(f"\nH2H Games Count:")
        print(f"  Mean: {df['h2h_games'].mean():.1f} prior games")
        print(f"  Max: {df['h2h_games'].max():.0f} prior games")
        print(f"  Games with no H2H history: {(df['h2h_games'] == 0).sum():,}")

# ============================================================================
# 9. TARGET VARIABLE ANALYSIS
# ============================================================================

def analyze_targets(df, save_plots=True):
    """Comprehensive target variable analysis."""
    print("\n" + "="*80)
    print("TARGET VARIABLE ANALYSIS")
    print("="*80)
    
    # Home win analysis
    if 'home_win' in df.columns:
        home_wins = df['home_win'].sum()
        total = len(df)
        print(f"\nHome Win Distribution:")
        print(f"  Home wins: {int(home_wins):,} ({home_wins/total:.2%})")
        print(f"  Away wins: {total - int(home_wins):,} ({(total-home_wins)/total:.2%})")
        
        # By season
        if 'season' in df.columns:
            print(f"\n  By Season:")
            for season in sorted(df['season'].unique()):
                season_df = df[df['season'] == season]
                win_rate = season_df['home_win'].mean()
                print(f"    {season}: {win_rate:.2%} ({len(season_df):,} games)")
    
    # Spread analysis
    if 'spread' in df.columns:
        print(f"\nSpread (Home - Away Points):")
        print(f"  Mean: {df['spread'].mean():+.2f} (home advantage)")
        print(f"  Median: {df['spread'].median():+.2f}")
        print(f"  Std: {df['spread'].std():.2f}")
        print(f"  Range: [{df['spread'].min():+.1f}, {df['spread'].max():+.1f}]")
        
        # Close games
        close_games = df[abs(df['spread']) <= 5]
        print(f"  Close games (≤5 pts): {len(close_games):,} ({len(close_games)/len(df):.1%})")
        
        # Blowouts
        blowouts = df[abs(df['spread']) > 20]
        print(f"  Blowouts (>20 pts): {len(blowouts):,} ({len(blowouts)/len(df):.1%})")
    
    # Total analysis
    if 'total' in df.columns:
        print(f"\nTotal Points (Home + Away):")
        print(f"  Mean: {df['total'].mean():.1f}")
        print(f"  Median: {df['total'].median():.1f}")
        print(f"  Std: {df['total'].std():.2f}")
        print(f"  Range: [{df['total'].min():.0f}, {df['total'].max():.0f}]")
    
    if save_plots:
        plot_target_distributions(df)

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_correlation_analysis(df, correlations):
    """Plot correlation analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Top correlations bar chart
    top_n = 20
    ax = axes[0, 0]
    top_corrs = correlations.head(top_n)
    colors = ['green' if x > 0 else 'red' for x in top_corrs.values]
    ax.barh(range(len(top_corrs)), top_corrs.values, color=colors, alpha=0.7)
    ax.set_yticks(range(len(top_corrs)))
    ax.set_yticklabels(top_corrs.index, fontsize=8)
    ax.set_xlabel('Correlation with home_win')
    ax.set_title(f'Top {top_n} Feature Correlations')
    ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
    ax.grid(axis='x', alpha=0.3)
    
    # Feature group correlations
    ax = axes[0, 1]
    group_corrs = []
    group_names = []
    for group_name, features in FEATURE_GROUPS.items():
        valid_features = [f for f in features if f in df.columns]
        if valid_features:
            avg_corr = abs(df[valid_features].corrwith(df['home_win'])).mean()
            group_corrs.append(avg_corr)
            group_names.append(group_name)
    
    ax.barh(range(len(group_names)), group_corrs, color='steelblue', alpha=0.7)
    ax.set_yticks(range(len(group_names)))
    ax.set_yticklabels(group_names)
    ax.set_xlabel('Average |Correlation|')
    ax.set_title('Feature Group Strength')
    ax.grid(axis='x', alpha=0.3)
    
    # Correlation distribution
    ax = axes[1, 0]
    ax.hist(correlations.values, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero correlation')
    ax.set_xlabel('Correlation with home_win')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Feature Correlations')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Scatter: net_rating_diff vs home_win
    ax = axes[1, 1]
    if 'net_rating_diff' in df.columns:
        # Bin net_rating_diff and calculate win rate
        bins = np.linspace(df['net_rating_diff'].min(), df['net_rating_diff'].max(), 30)
        df['net_rating_bin'] = pd.cut(df['net_rating_diff'], bins=bins)
        win_rate_by_bin = df.groupby('net_rating_bin')['home_win'].mean()
        bin_centers = [interval.mid for interval in win_rate_by_bin.index]
        
        ax.scatter(bin_centers, win_rate_by_bin.values, alpha=0.6, s=100, color='steelblue')
        ax.axhline(0.5, color='red', linestyle='--', linewidth=1, label='50% baseline')
        ax.set_xlabel('Net Rating Differential')
        ax.set_ylabel('Home Win Rate')
        ax.set_title('Win Rate by Net Rating Differential')
        ax.legend()
        ax.grid(alpha=0.3)
        
        df.drop('net_rating_bin', axis=1, inplace=True)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}correlation_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {OUTPUT_DIR}correlation_analysis.png")
    plt.close()

def plot_four_factors(df, factors):
    """Plot Four Factors analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.ravel()
    
    for i, factor in enumerate(factors):
        if factor not in df.columns:
            continue
        
        ax = axes[i]
        
        # Box plots by outcome
        home_wins = df[df['home_win'] == 1][factor]
        home_losses = df[df['home_win'] == 0][factor]
        
        bp = ax.boxplot([home_wins, home_losses], labels=['Home Win', 'Home Loss'],
                        patch_artist=True, showfliers=False)
        
        for patch, color in zip(bp['boxes'], ['lightgreen', 'lightcoral']):
            patch.set_facecolor(color)
        
        # Add correlation
        corr = df[factor].corr(df['home_win'])
        ax.set_title(f'{factor}\n(r = {corr:+.4f})', fontsize=10)
        ax.set_ylabel('Value')
        ax.grid(axis='y', alpha=0.3)
        ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}four_factors_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {OUTPUT_DIR}four_factors_analysis.png")
    plt.close()

def plot_rest_analysis(df):
    """Plot rest and fatigue analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Rest advantage distribution
    ax = axes[0, 0]
    if 'rest_advantage' in df.columns:
        ax.hist(df['rest_advantage'], bins=30, color='steelblue', alpha=0.7, edgecolor='black')
        ax.axvline(df['rest_advantage'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["rest_advantage"].mean():.2f}')
        ax.set_xlabel('Rest Advantage (days)')
        ax.set_ylabel('Frequency')
        ax.set_title('Rest Advantage Distribution')
        ax.legend()
        ax.grid(alpha=0.3)
    
    # B2B impact
    ax = axes[0, 1]
    if 'home_b2b' in df.columns and 'away_b2b' in df.columns:
        b2b_scenarios = [
            ('Neither B2B', (df['home_b2b']==0) & (df['away_b2b']==0)),
            ('Home B2B', (df['home_b2b']==1) & (df['away_b2b']==0)),
            ('Away B2B', (df['home_b2b']==0) & (df['away_b2b']==1)),
            ('Both B2B', (df['home_b2b']==1) & (df['away_b2b']==1))
        ]
        
        labels = []
        win_rates = []
        counts = []
        
        for label, mask in b2b_scenarios:
            subset = df[mask]
            if len(subset) > 0:
                labels.append(f'{label}\n(n={len(subset)})')
                win_rates.append(subset['home_win'].mean())
                counts.append(len(subset))
        
        bars = ax.bar(range(len(labels)), win_rates, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel('Home Win Rate')
        ax.set_title('Win Rate by B2B Scenario')
        ax.axhline(0.5, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.grid(axis='y', alpha=0.3)
        
        for i, (bar, rate) in enumerate(zip(bars, win_rates)):
            ax.text(i, rate, f'{rate:.1%}', ha='center', va='bottom', fontsize=9)
    
    # Win rate by rest advantage buckets
    ax = axes[1, 0]
    if 'rest_advantage' in df.columns:
        rest_bins = [-10, -3, -1, 0, 1, 3, 10]
        df['rest_bucket'] = pd.cut(df['rest_advantage'], bins=rest_bins)
        win_rate_by_rest = df.groupby('rest_bucket')['home_win'].agg(['mean', 'count'])
        
        x_labels = [f'{interval}' for interval in win_rate_by_rest.index]
        x_pos = range(len(x_labels))
        
        bars = ax.bar(x_pos, win_rate_by_rest['mean'], color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('Home Win Rate')
        ax.set_title('Win Rate by Rest Advantage')
        ax.axhline(0.5, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.grid(axis='y', alpha=0.3)
        
        for i, (bar, rate, count) in enumerate(zip(bars, win_rate_by_rest['mean'], win_rate_by_rest['count'])):
            ax.text(i, rate, f'{rate:.2%}\n(n={count})', ha='center', va='bottom', fontsize=7)
        
        df.drop('rest_bucket', axis=1, inplace=True)
    
    # Correlation of rest features
    ax = axes[1, 1]
    rest_features = [f for f in FEATURE_GROUPS["Rest & Fatigue"] if f in df.columns]
    if rest_features:
        corrs = [df[f].corr(df['home_win']) for f in rest_features]
        colors = ['green' if c > 0 else 'red' for c in corrs]
        
        ax.barh(range(len(rest_features)), corrs, color=colors, alpha=0.7, edgecolor='black')
        ax.set_yticks(range(len(rest_features)))
        ax.set_yticklabels(rest_features, fontsize=8)
        ax.set_xlabel('Correlation with home_win')
        ax.set_title('Rest Feature Correlations')
        ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}rest_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {OUTPUT_DIR}rest_analysis.png")
    plt.close()

def plot_target_distributions(df):
    """Plot target variable distributions."""
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    # Home win distribution
    ax = axes[0, 0]
    if 'home_win' in df.columns:
        counts = df['home_win'].value_counts().sort_index()
        bars = ax.bar(['Away Win', 'Home Win'], counts.values, 
                     color=['#ff7f0e', '#1f77b4'], alpha=0.7, edgecolor='black')
        ax.set_ylabel('Count')
        ax.set_title('Home Win Distribution')
        
        for i, (bar, count) in enumerate(zip(bars, counts.values)):
            pct = count / len(df) * 100
            ax.text(i, count, f'{count:,}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
    
    # Spread distribution
    ax = axes[0, 1]
    if 'spread' in df.columns:
        ax.hist(df['spread'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
        ax.axvline(df['spread'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["spread"].mean():+.1f}')
        ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
        ax.set_xlabel('Spread (Home - Away)')
        ax.set_ylabel('Frequency')
        ax.set_title('Point Spread Distribution')
        ax.legend()
        ax.grid(alpha=0.3)
    
    # Total distribution
    ax = axes[0, 2]
    if 'total' in df.columns:
        ax.hist(df['total'], bins=50, color='green', alpha=0.7, edgecolor='black')
        ax.axvline(df['total'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["total"].mean():.1f}')
        ax.set_xlabel('Total Points')
        ax.set_ylabel('Frequency')
        ax.set_title('Total Points Distribution')
        ax.legend()
        ax.grid(alpha=0.3)
    
    # Home/Away points by outcome
    ax = axes[1, 0]
    if 'home_pts' in df.columns and 'away_pts' in df.columns:
        home_wins = df[df['home_win'] == 1]
        home_losses = df[df['home_win'] == 0]
        
        bp = ax.boxplot(
            [home_wins['home_pts'], home_losses['home_pts'],
             home_wins['away_pts'], home_losses['away_pts']],
            labels=['Home\n(Win)', 'Home\n(Loss)', 'Away\n(Win)', 'Away\n(Loss)'],
            patch_artist=True, showfliers=False
        )
        
        for patch, color in zip(bp['boxes'], 
                                ['lightgreen', 'lightcoral', 'lightcoral', 'lightgreen']):
            patch.set_facecolor(color)
        
        ax.set_ylabel('Points')
        ax.set_title('Points by Team and Outcome')
        ax.grid(axis='y', alpha=0.3)
    
    # Spread by season
    ax = axes[1, 1]
    if 'spread' in df.columns and 'season' in df.columns:
        seasons = sorted(df['season'].unique())
        spread_by_season = [df[df['season'] == s]['spread'] for s in seasons]
        
        bp = ax.boxplot(spread_by_season, labels=seasons, patch_artist=True, showfliers=False)
        for patch in bp['boxes']:
            patch.set_facecolor('steelblue')
        
        ax.set_xlabel('Season')
        ax.set_ylabel('Spread')
        ax.set_title('Spread Distribution by Season')
        ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='y', alpha=0.3)
    
    # Win rate by season
    ax = axes[1, 2]
    if 'home_win' in df.columns and 'season' in df.columns:
        win_rates = df.groupby('season')['home_win'].mean()
        counts = df.groupby('season').size()
        
        bars = ax.bar(range(len(win_rates)), win_rates.values, 
                     color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xticks(range(len(win_rates)))
        ax.set_xticklabels(win_rates.index, rotation=45, ha='right')
        ax.set_ylabel('Home Win Rate')
        ax.set_title('Home Win Rate by Season')
        ax.axhline(0.5, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.grid(axis='y', alpha=0.3)
        
        for i, (bar, rate, count) in enumerate(zip(bars, win_rates.values, counts.values)):
            ax.text(i, rate, f'{rate:.1%}\n(n={count})', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}target_distributions.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {OUTPUT_DIR}target_distributions.png")
    plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run comprehensive EDA."""
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    df = load_and_inspect(DATA_PATH)
    
    # Data quality
    df = assess_data_quality(df)
    
    # Correlations
    correlations = analyze_correlations(df, save_plots=True)
    
    # Four Factors
    four_factors_df = analyze_four_factors(df, save_plots=True)
    
    # Rolling windows
    analyze_rolling_features(df)
    
    # Rest analysis
    analyze_rest_features(df, save_plots=True)
    
    # Momentum
    analyze_momentum(df)
    
    # Head-to-head
    analyze_h2h(df)
    
    # Targets
    analyze_targets(df, save_plots=True)
    
    print("\n" + "="*80)
    print("EDA COMPLETE!")
    print("="*80)
    print(f"\nVisualizations saved to: {OUTPUT_DIR}")
    print("\nGenerated files:")
    print("  - correlation_analysis.png")
    print("  - four_factors_analysis.png")
    print("  - rest_analysis.png")
    print("  - target_distributions.png")
    
    return df

if __name__ == "__main__":
    df = main()