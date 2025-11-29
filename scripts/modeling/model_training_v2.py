"""
CORRECTED NBA PREDICTION MODEL TRAINING
========================================

This fixes the feature extraction bug that was causing poor performance.

Expected results after fix:
- Accuracy: 68-75% (vs your 60.4%)
- Log Loss: <0.60 (vs your 0.759)
- AUC: >0.70 (vs your 0.651)
"""

import pandas as pd
from datetime import datetime
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
import numpy as np


def load_and_split_data(csv_path="C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\final\\nba_train_data_enhanced.csv"):
    """Load data and create 70/15/15 split."""
    print("=" * 80)
    print("LOADING DATA")
    print("=" * 80)
    
    df = pd.read_csv(csv_path)
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df = df.sort_values("GAME_DATE").reset_index(drop=True)
    
    print(f"Total games: {len(df):,}")
    print(f"Date range: {df['GAME_DATE'].min()} to {df['GAME_DATE'].max()}")

    total = len(df)
    val_idx = int(total * 0.70)
    test_idx = int(total * 0.85)

    train_df = df.iloc[:val_idx].copy()
    val_df = df.iloc[val_idx:test_idx].copy()
    test_df = df.iloc[test_idx:].copy()
    
    print(f"\nTrain: {len(train_df):,} games ({len(train_df)/total*100:.1f}%)")
    print(f"Val:   {len(val_df):,} games ({len(val_df)/total*100:.1f}%)")
    print(f"Test:  {len(test_df):,} games ({len(test_df)/total*100:.1f}%)")

    X_train, y_train = extract_features(train_df, "TRAINING")
    X_val, y_val = extract_features(val_df, "VALIDATION")
    X_test, y_test = extract_features(test_df, "TEST")

    return X_train, y_train, X_val, y_val, X_test, y_test, train_df, val_df, test_df


def extract_features(df, dataset_name=""):
    """
    CORRECTED feature extraction - keeps _PRIOR and _DIFF features!
    
    WHAT WE KEEP:
    ✅ All *_PRIOR columns (pre-game statistics)
    ✅ All *_DIFF columns (matchup differentials)
    ✅ REST_ADVANTAGE, HOME_B2B, AWAY_B2B
    ✅ HOME_DAYS_REST, AWAY_DAYS_REST
    ✅ HOME_SEASON_PROGRESS, AWAY_SEASON_PROGRESS
    
    WHAT WE REMOVE:
    ❌ Game metadata (team names, IDs, dates)
    ❌ Game results from THIS game (PTS, FGM, AST, etc.)
    ❌ Season stats WITHOUT _PRIOR (include current game = leakage)
    """
    
    # Metadata
    metadata = [
        "GAME_ID", "GAME_DATE", "SEASON",
        "HOME_TEAM_ID", "HOME_TEAM_ABBREVIATION", "HOME_TEAM_NAME",
        "AWAY_TEAM_ID", "AWAY_TEAM_ABBREVIATION", "AWAY_TEAM_NAME",
        "HOME_WL", "AWAY_WL",
    ]
    
    # Game results (THIS game's outcomes)
    game_results = [
        "HOME_PTS", "AWAY_PTS", "HOME_PLUS_MINUS", "AWAY_PLUS_MINUS",
        "HOME_FGM", "HOME_FGA", "HOME_FG_PCT", "HOME_FG3M", "HOME_FG3A", "HOME_FG3_PCT",
        "HOME_FTM", "HOME_FTA", "HOME_FT_PCT", "HOME_OREB", "HOME_DREB", "HOME_REB",
        "HOME_AST", "HOME_STL", "HOME_BLK", "HOME_TOV", "HOME_PF",
        "AWAY_FGM", "AWAY_FGA", "AWAY_FG_PCT", "AWAY_FG3M", "AWAY_FG3A", "AWAY_FG3_PCT",
        "AWAY_FTM", "AWAY_FTA", "AWAY_FT_PCT", "AWAY_OREB", "AWAY_DREB", "AWAY_REB",
        "AWAY_AST", "AWAY_STL", "AWAY_BLK", "AWAY_TOV", "AWAY_PF",
    ]
    
    # Season stats WITHOUT _PRIOR (include current game - data leakage!)
    # NOTE: We KEEP the _PRIOR versions!
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
    
    # Combine exclusions
    exclude = metadata + game_results + season_stats_non_prior + ["HOME_WIN"]
    exclude = [c for c in exclude if c in df.columns]
    
    X = df.drop(columns=exclude)
    y = df["HOME_WIN"]
    
    # Verification
    if dataset_name:
        print(f"\n{dataset_name} SET:")
        print(f"  Features: {X.shape[1]}")
        
        # Count feature types
        prior_features = [col for col in X.columns if '_PRIOR' in col]
        diff_features = [col for col in X.columns if '_DIFF' in col]
        rest_features = [col for col in X.columns if 'REST' in col or 'B2B' in col]
        
        print(f"  - PRIOR features: {len(prior_features)}")
        print(f"  - DIFF features: {len(diff_features)}")
        print(f"  - REST features: {len(rest_features)}")
        
        # Check critical features
        critical = ['NET_RATING_DIFF', 'WIN_PCT_DIFF']
        missing_critical = [f for f in critical if f not in X.columns]
        if missing_critical:
            print(f"  ⚠️  WARNING: Missing critical features: {missing_critical}")
        else:
            print(f"  ✅ All critical features present")
    
    return X, y


def evaluate(model, X, y, dataset_name=""):
    """Evaluate model and print comprehensive metrics."""
    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1]

    acc = accuracy_score(y, pred)
    ll = log_loss(y, proba)
    auc = roc_auc_score(y, proba)
    
    baseline = y.mean()  # Home team win rate

    print(f"\n{dataset_name} RESULTS:")
    print(f"  Accuracy:  {acc:.3f} ({acc:.1%})")
    print(f"  Baseline:  {baseline:.3f} ({baseline:.1%}) [home team always wins]")
    print(f"  Lift:      {(acc-baseline)*100:+.1f} percentage points")
    print(f"  Log Loss:  {ll:.3f}", end="")
    if ll < 0.55:
        print(" 🌟 EXCELLENT")
    elif ll < 0.60:
        print(" ✅ GOOD")
    elif ll < 0.65:
        print(" ⚠️  ACCEPTABLE")
    else:
        print(" ❌ NEEDS IMPROVEMENT")
    
    print(f"  ROC AUC:   {auc:.3f}", end="")
    if auc > 0.75:
        print(" 🌟 EXCELLENT")
    elif auc > 0.70:
        print(" ✅ GOOD")
    elif auc > 0.65:
        print(" ⚠️  ACCEPTABLE")
    else:
        print(" ❌ NEEDS IMPROVEMENT")
    
    # Overall assessment
    print(f"\n  OVERALL:", end=" ")
    if acc >= 0.73 and ll < 0.58:
        print("🌟 EXCELLENT - Production ready!")
    elif acc >= 0.68 and ll < 0.62:
        print("✅ GOOD - Above target performance")
    elif acc >= 0.65 and ll < 0.67:
        print("⚠️  ACCEPTABLE - Room for improvement")
    else:
        print("❌ BELOW TARGET - Check features and model")

    return acc, ll, auc


def plot_calibration(y_true, y_pred_proba, n_bins=10, save_path=None):
    """Plot calibration curve."""
    prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=n_bins)

    plt.figure(figsize=(10, 8))
    plt.plot(prob_pred, prob_true, marker="o", linewidth=2, markersize=8, label='Model')
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label='Perfect calibration')
    plt.xlabel("Predicted Probability", fontsize=12)
    plt.ylabel("Actual Win Rate", fontsize=12)
    plt.title("Calibration Curve - Model Probability Accuracy", fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"\n✅ Calibration curve saved to {save_path}")

    plt.show()


def plot_feature_importance(model, X, top_n=20, save_path=None):
    """Plot top N most important features."""
    importance = model.feature_importances_
    feature_names = X.columns
    
    # Create dataframe and sort
    feat_imp = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False).head(top_n)
    
    # Plot
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(feat_imp)), feat_imp['importance'])
    plt.yticks(range(len(feat_imp)), feat_imp['feature'])
    plt.xlabel('Importance', fontsize=12)
    plt.title(f'Top {top_n} Most Important Features', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"✅ Feature importance saved to {save_path}")
    
    plt.show()
    
    # Print top features
    print("\nTOP 10 MOST IMPORTANT FEATURES:")
    for i, row in feat_imp.head(10).iterrows():
        print(f"  {row['feature']:40s} {row['importance']:.4f}")


def main():
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "NBA PREDICTION MODEL - CORRECTED VERSION" + " " * 23 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Load and split data
    X_train, y_train, X_val, y_val, X_test, y_test, train_df, val_df, test_df = load_and_split_data()
    
    # Train model
    print("\n" + "=" * 80)
    print("TRAINING XGBOOST MODEL")
    print("=" * 80)
    
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        tree_method="hist",
        random_state=42,
    )
    
    print("\nTraining...")
    model.fit(X_train, y_train)
    print("✅ Training complete")
    
    # Evaluate
    print("\n" + "=" * 80)
    print("EVALUATION")
    print("=" * 80)
    
    val_acc, val_ll, val_auc = evaluate(model, X_val, y_val, "VALIDATION")
    test_acc, test_ll, test_auc = evaluate(model, X_test, y_test, "TEST")
    
    # Feature importance
    print("\n" + "=" * 80)
    print("FEATURE IMPORTANCE")
    print("=" * 80)
    plot_feature_importance(model, X_train, top_n=20, save_path="feature_importance.png")
    
    # Calibration curve
    print("\n" + "=" * 80)
    print("CALIBRATION CURVE")
    print("=" * 80)
    proba_test = model.predict_proba(X_test)[:, 1]
    plot_calibration(y_test, proba_test, save_path="calibration.png")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nValidation: {val_acc:.1%} accuracy, {val_ll:.3f} log loss, {val_auc:.3f} AUC")
    print(f"Test:       {test_acc:.1%} accuracy, {test_ll:.3f} log loss, {test_auc:.3f} AUC")
    
    print("\n" + "=" * 80)
    print("COMPARISON TO YOUR PREVIOUS RESULTS")
    print("=" * 80)
    print("\nYour previous (incorrect) results:")
    print("  Val:  60.4% accuracy, 0.759 log loss, 0.651 AUC ❌")
    print("  Test: 61.5% accuracy, 0.702 log loss, 0.679 AUC ❌")
    
    print("\nCorrected results (this run):")
    print(f"  Val:  {val_acc:.1%} accuracy, {val_ll:.3f} log loss, {val_auc:.3f} AUC")
    print(f"  Test: {test_acc:.1%} accuracy, {test_ll:.3f} log loss, {test_auc:.3f} AUC")
    
    improvement = (test_acc - 0.615) * 100
    print(f"\n📈 Improvement: {improvement:+.1f} percentage points in accuracy!")
    
    if test_acc >= 0.68 and test_ll < 0.62:
        print("\n🎉 SUCCESS! Model meets target performance!")
    elif test_acc >= 0.65:
        print("\n✓ Good progress! Try hyperparameter tuning for further improvement.")
    else:
        print("\n⚠️  Still below target. Check data quality and features.")


if __name__ == "__main__":
    main()