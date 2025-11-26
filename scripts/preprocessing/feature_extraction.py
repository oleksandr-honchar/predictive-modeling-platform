"""
CORRECTED FEATURE EXTRACTION
=============================

The issue: You were excluding ALL season stats, including the _PRIOR features
which are your main predictors!

Fix: Only exclude NON-PRIOR season stats (which include the current game result)
"""

def extract_features(df):
    """
    Extract features, keeping only legitimate predictors.
    
    KEEP (these are predictive):
    - All *_PRIOR columns (pre-game stats)
    - All *_DIFF columns (matchup differentials)
    - REST_ADVANTAGE, HOME_B2B, AWAY_B2B
    - HOME_DAYS_REST, AWAY_DAYS_REST
    - HOME_SEASON_PROGRESS, AWAY_SEASON_PROGRESS
    
    REMOVE (these cause data leakage):
    - Game metadata (team names, IDs, dates)
    - Game results (PTS, FGM, AST, etc. from THIS game)
    - Season stats WITHOUT _PRIOR (include current game)
    """
    
    # 1. Metadata columns
    metadata = [
        "GAME_ID", "GAME_DATE", "SEASON",
        "HOME_TEAM_ID", "HOME_TEAM_ABBREVIATION", "HOME_TEAM_NAME",
        "AWAY_TEAM_ID", "AWAY_TEAM_ABBREVIATION", "AWAY_TEAM_NAME",
        "HOME_WL", "AWAY_WL",
    ]
    
    # 2. Game result columns (THIS game's box score)
    game_results = [
        "HOME_PTS", "AWAY_PTS", "HOME_PLUS_MINUS", "AWAY_PLUS_MINUS",
        "HOME_FGM", "HOME_FGA", "HOME_FG_PCT", "HOME_FG3M", "HOME_FG3A", "HOME_FG3_PCT",
        "HOME_FTM", "HOME_FTA", "HOME_FT_PCT", "HOME_OREB", "HOME_DREB", "HOME_REB",
        "HOME_AST", "HOME_STL", "HOME_BLK", "HOME_TOV", "HOME_PF",
        "AWAY_FGM", "AWAY_FGA", "AWAY_FG_PCT", "AWAY_FG3M", "AWAY_FG3A", "AWAY_FG3_PCT",
        "AWAY_FTM", "AWAY_FTA", "AWAY_FT_PCT", "AWAY_OREB", "AWAY_DREB", "AWAY_REB",
        "AWAY_AST", "AWAY_STL", "AWAY_BLK", "AWAY_TOV", "AWAY_PF",
    ]
    
    # 3. Season stats WITHOUT _PRIOR (these INCLUDE current game - leakage!)
    # NOTE: We KEEP the _PRIOR versions - those are our predictors!
    season_stats_non_prior = [
        "HOME_GP", "HOME_W", "HOME_L", "HOME_W_PCT", "HOME_MIN_SEASON",
        "HOME_E_OFF_RATING", "HOME_OFF_RATING", "HOME_E_DEF_RATING", "HOME_DEF_RATING",
        "HOME_E_NET_RATING", "HOME_NET_RATING", "HOME_AST_PCT", "HOME_AST_TO",
        "HOME_AST_RATIO", "HOME_DREB_PCT", "HOME_REB_PCT", "HOME_TS_PCT",
        "HOME_E_PACE", "HOME_PACE", "HOME_PACE_PER40", "HOME_POSS", "HOME_PIE",
        "HOME_EFG_PCT_FF", "HOME_FTA_RATE", "HOME_TM_TOV_PCT_FF", "HOME_OREB_PCT_FF",
        "HOME_OPP_EFG_PCT", "HOME_OPP_FTA_RATE", "HOME_OPP_TOV_PCT", "HOME_OPP_OREB_PCT",
        "AWAY_GP", "AWAY_W", "AWAY_L", "AWAY_W_PCT", "AWAY_MIN_SEASON",
        "AWAY_E_OFF_RATING", "AWAY_OFF_RATING", "AWAY_E_DEF_RATING", "AWAY_DEF_RATING",
        "AWAY_E_NET_RATING", "AWAY_NET_RATING", "AWAY_AST_PCT", "AWAY_AST_TO",
        "AWAY_AST_RATIO", "AWAY_DREB_PCT", "AWAY_REB_PCT", "AWAY_TS_PCT",
        "AWAY_E_PACE", "AWAY_PACE", "AWAY_PACE_PER40", "AWAY_POSS", "AWAY_PIE",
        "AWAY_EFG_PCT_FF", "AWAY_FTA_RATE", "AWAY_TM_TOV_PCT_FF", "AWAY_OREB_PCT_FF",
        "AWAY_OPP_EFG_PCT", "AWAY_OPP_FTA_RATE", "AWAY_OPP_TOV_PCT", "AWAY_OPP_OREB_PCT",
    ]
    
    # Combine all exclusions
    exclude = metadata + game_results + season_stats_non_prior + ["HOME_WIN"]
    exclude = [c for c in exclude if c in df.columns]
    
    X = df.drop(columns=exclude)
    y = df["HOME_WIN"]
    
    # Verify we kept important features
    print(f"\n✅ Features extracted: {X.shape[1]} columns")
    
    # Check for key predictors
    key_features = [col for col in X.columns if '_PRIOR' in col or '_DIFF' in col]
    print(f"✅ Predictive features (PRIOR/DIFF): {len(key_features)}")
    
    # Show sample features
    print(f"\nSample features kept:")
    for col in list(X.columns)[:10]:
        print(f"  - {col}")
    
    return X, y


# Test the corrected function
if __name__ == "__main__":
    import pandas as pd
    
    # Load your data
    csv_path = "C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\nba_training_data.csv"
    df = pd.read_csv(csv_path)
    
    print("=" * 80)
    print("TESTING CORRECTED FEATURE EXTRACTION")
    print("=" * 80)
    
    X, y = extract_features(df)
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Check for critical features
    must_have = ['NET_RATING_DIFF', 'WIN_PCT_DIFF', 'HOME_NET_RATING_PRIOR', 'AWAY_NET_RATING_PRIOR']
    for feat in must_have:
        if feat in X.columns:
            print(f"✅ {feat} - FOUND (good!)")
        else:
            print(f"❌ {feat} - MISSING (bad!)")
    
    print(f"\nTotal features: {X.shape[1]}")
    print(f"Target variable: {y.name} with {y.sum()} home wins ({y.mean():.1%})")