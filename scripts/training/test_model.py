"""
Prediction-Optimized Feature Engineering & Evaluation
(No betting/wagering code included)

Usage:
    df = pd.read_csv("data/processed/nba/final/nba_train_data_enhanced.csv", parse_dates=['GAME_DATE'])
    df_fe = build_prediction_features(df)
    train_df, val_df, test_df = temporal_split(df_fe)
    model, calibrator = train_and_calibrate(train_df, val_df, feature_cols, target_col='TARGET')
    evaluate_model(model, calibrator, test_df, feature_cols, target_col='TARGET')
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, log_loss, roc_auc_score, brier_score_loss,
    precision_recall_fscore_support
)
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="darkgrid")
plt.style.use("dark_background")


# ---------------------------
# Helpers
# ---------------------------
def temporal_split(df, date_col="GAME_DATE", train_frac=0.70, val_frac=0.15):
    df = df.sort_values(date_col).reset_index(drop=True)
    n = len(df)
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))
    return df.iloc[:train_end].reset_index(drop=True), df.iloc[train_end:val_end].reset_index(drop=True), df.iloc[val_end:].reset_index(drop=True)


def weighted_rolling(series, window, weights=None, min_periods=1):
    if weights is None:
        return series.rolling(window, min_periods=min_periods).mean()
    w = np.array(weights[-window:])
    def apply_roll(x):
        valid = ~np.isnan(x)
        if valid.sum() == 0:
            return np.nan
        vals = x[valid]
        ww = w[-len(vals):]
        return (vals * ww).sum() / ww.sum()
    return series.rolling(window, min_periods=min_periods).apply(lambda x: apply_roll(x), raw=True)


# ---------------------------
# Core feature builder
# ---------------------------
def build_prediction_features(df):
    df = df.copy()
    # Basic target
    if "HOME_WIN" in df.columns:
        df["TARGET"] = df["HOME_WIN"].astype(int)
    else:
        raise ValueError("HOME_WIN column required")

    # Ensure chronological grouping by season
    df = df.sort_values(['SEASON', 'GAME_DATE']).reset_index(drop=True)

    # ---------- 1) Per-team rolling windows (weighted) ----------
    # windows: recent emphasis (3,5,10,20)
    windows = [3, 5, 10, 20]
    numeric_base = [
        "HOME_PTS", "AWAY_PTS", "HOME_OFF_RATING_PRIOR", "HOME_DEF_RATING_PRIOR",
        "AWAY_OFF_RATING_PRIOR", "AWAY_DEF_RATING_PRIOR",
        "HOME_EFG_PCT_FF_PRIOR", "AWAY_EFG_PCT_FF_PRIOR",
        "HOME_FTA_RATE_PRIOR", "AWAY_FTA_RATE_PRIOR",
        "HOME_TM_TOV_PCT_FF_PRIOR", "AWAY_TM_TOV_PCT_FF_PRIOR",
        "HOME_OREB_PCT_FF_PRIOR", "AWAY_OREB_PCT_FF_PRIOR",
    ]

    # For each team we compute rolling means for their team-specific columns.
    # We'll build for HOME and AWAY separately and shift(1) to avoid leakage.
    def team_rolling(df, team_id_col, prefix, stats_to_use):
        # Create a frame keyed by team-season-game order
        df_temp = df[[team_id_col, 'SEASON', 'GAME_DATE'] + stats_to_use].copy()
        df_temp = df_temp.rename(columns={team_id_col: 'TEAM_ID'})
        df_temp = df_temp.sort_values(['TEAM_ID', 'SEASON', 'GAME_DATE'])
        out = pd.DataFrame(index=df_temp.index)
        for w in windows:
            # exponential weights: more weight to recent games
            weights = np.exp(np.linspace(-1, 0, w))
            for col in stats_to_use:
                roll = (
                    df_temp.groupby(['TEAM_ID', 'SEASON'])[col]
                    .apply(lambda s: weighted_rolling(s, w, weights, min_periods=1))
                    .shift(1)  # shift to keep only prior info (pre-game)
                )
                out[f"{prefix}_{col}_R{w}"] = roll.values
        out.index = df_temp.index
        return out, df_temp.index

    # Map HOME stats names to their team-level columns
    home_stats = [
        'HOME_PTS', 'HOME_OFF_RATING_PRIOR', 'HOME_DEF_RATING_PRIOR',
        'HOME_EFG_PCT_FF_PRIOR', 'HOME_FTA_RATE_PRIOR',
        'HOME_TM_TOV_PCT_FF_PRIOR', 'HOME_OREB_PCT_FF_PRIOR'
    ]
    away_stats = [
        'AWAY_PTS', 'AWAY_OFF_RATING_PRIOR', 'AWAY_DEF_RATING_PRIOR',
        'AWAY_EFG_PCT_FF_PRIOR', 'AWAY_FTA_RATE_PRIOR',
        'AWAY_TM_TOV_PCT_FF_PRIOR', 'AWAY_OREB_PCT_FF_PRIOR'
    ]

    # Build HOME team rolling
    home_rows = df.reset_index()
    home_rows['TEAM_ID'] = home_rows['HOME_TEAM_ID']
    home_rows_stats = home_rows[['TEAM_ID', 'SEASON', 'GAME_DATE'] + home_stats].copy()
    home_out = pd.DataFrame(index=home_rows.index)
    for w in windows:
        weights = np.exp(np.linspace(-1, 0, w))
        for col in home_stats:
            series = (
                home_rows.groupby(['HOME_TEAM_ID', 'SEASON'])[col]
                .apply(lambda s: weighted_rolling(s, w, weights, min_periods=1))
                .shift(1)
            )
            home_out[f"H_{col}_R{w}"] = series.values

    # Build AWAY team rolling
    away_rows = df.reset_index()
    away_rows['TEAM_ID'] = away_rows['AWAY_TEAM_ID']
    away_out = pd.DataFrame(index=away_rows.index)
    for w in windows:
        weights = np.exp(np.linspace(-1, 0, w))
        for col in away_stats:
            series = (
                away_rows.groupby(['AWAY_TEAM_ID', 'SEASON'])[col]
                .apply(lambda s: weighted_rolling(s, w, weights, min_periods=1))
                .shift(1)
            )
            away_out[f"A_{col}_R{w}"] = series.values

    # Merge rolling features back
    df = df.reset_index(drop=True)
    df = pd.concat([df, home_out.reset_index(drop=True), away_out.reset_index(drop=True)], axis=1)

    # ---------- 2) Elo-like ratings (team-level, season-reset) ----------
    # Simple Elo: initialize at 1500 per season, update by margin and K scaled by schedule importance
    def compute_elo(df, k=20):
        df = df.sort_values(['SEASON', 'GAME_DATE']).copy()
        teams = pd.concat([df['HOME_TEAM_ID'], df['AWAY_TEAM_ID']]).unique()
        elo = {}  # (team, season) -> elo
        elo_home = []
        elo_away = []
        for _, row in df.iterrows():
            season = row['SEASON']
            h = row['HOME_TEAM_ID']
            a = row['AWAY_TEAM_ID']
            key_h = (h, season)
            key_a = (a, season)
            if key_h not in elo:
                elo[key_h] = 1500.0
            if key_a not in elo:
                elo[key_a] = 1500.0
            Eh = 1 / (1 + 10 ** ((elo[key_a] - elo[key_h]) / 400))
            Ea = 1 - Eh
            # Save pre-game elos
            elo_home.append(elo[key_h])
            elo_away.append(elo[key_a])
            # Margin multiplier (caps)
            margin = row['HOME_PTS'] - row['AWAY_PTS'] if 'HOME_PTS' in row else 0
            mult = np.log(abs(margin) + 1) * (2.2 / ((row.get('HOME_POSS', 100) + 1) * 0.001 + 2.2))
            # Update
            S_h = 1.0 if row['HOME_WIN'] == 1 else 0.0
            elo[key_h] += k * mult * (S_h - Eh)
            elo[key_a] += k * mult * ((1 - S_h) - Ea)
        df['ELO_HOME_PRE'] = elo_home
        df['ELO_AWAY_PRE'] = elo_away
        return df

    df = compute_elo(df)

    # ---------- 3) Opponent-adjusted metrics ----------
    # Example: team's net rating minus opponent's average net rating prior (already have _PRIOR cols)
    df['HOME_NET_MINUS_OPPAVG'] = df['HOME_NET_RATING_PRIOR'] - df['AWAY_NET_RATING_PRIOR']
    df['AWAY_NET_MINUS_OPPAVG'] = df['AWAY_NET_RATING_PRIOR'] - df['HOME_NET_RATING_PRIOR']

    # ---------- 4) Rest and travel interactions ----------
    # Rest advantage as numeric and flags already exist in dataset (HOME_DAYS_REST, AWAY_DAYS_REST, HOME_B2B, AWAY_B2B)
    df['REST_DIFF'] = df['HOME_DAYS_REST'] - df['AWAY_DAYS_REST']
    df['HOME_B2B_FLAG'] = df['HOME_B2B'].astype(int)
    df['AWAY_B2B_FLAG'] = df['AWAY_B2B'].astype(int)
    df['EXTREME_REST'] = (df['REST_DIFF'].abs() >= 3).astype(int)

    # ---------- 5) Interaction features (nonlinear signals) ----------
    # Interaction examples shown; pick a few high-signal interactions to avoid explosion
    df['ELO_DIFF'] = df['ELO_HOME_PRE'] - df['ELO_AWAY_PRE']
    df['NET_RATING_DIFF_PRIOR'] = df['HOME_NET_RATING_PRIOR'] - df['AWAY_NET_RATING_PRIOR']
    df['ELO_NET_INTERACT'] = df['ELO_DIFF'] * df['NET_RATING_DIFF_PRIOR']
    df['PACE_DIFF'] = df['HOME_PACE_PRIOR'] - df['AWAY_PACE_PRIOR']
    df['PACE_X_REST'] = df['PACE_DIFF'] * df['REST_DIFF']

    # ---------- 6) Fill remaining NaNs sensibly (no arbitrary zeros) ----------
    # For rolling stats use lower-window fallback: prefer R3 -> R5 -> R10 -> R20 (if missing)
    roll_cols = [c for c in df.columns if "_R" in c and ("H_" in c or "A_" in c)]
    # Group by stat stem and fill
    for stat in ['HOME_PTS', 'AWAY_PTS', 'HOME_OFF_RATING_PRIOR', 'AWAY_OFF_RATING_PRIOR',
                 'HOME_DEF_RATING_PRIOR', 'AWAY_DEF_RATING_PRIOR']:
        # attempt to fill hierarchically for home and away
        for side in ['H_', 'A_']:
            candidates = [f"{side}{stat}_R{w}" for w in windows if f"{side}{stat}_R{w}" in df.columns]
            if not candidates:
                continue
            # hierarchical fill: smaller window -> larger
            df[f"FE_{side}{stat}_ROLL_FALLBACK"] = df[candidates].bfill(axis=1).iloc[:, 0]

    # For any remaining numeric NaN, fill with team-season median for that column where possible
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col] = df.groupby('SEASON')[col].transform(lambda x: x.fillna(x.median()))

            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())

    # ---------- 7) Model features selection (compact) ----------
    feature_cols = [
        'ELO_DIFF',
        'NET_RATING_DIFF_PRIOR',
        'ELO_NET_INTERACT',
        'FE_H_HOME_PTS_ROLL_FALLBACK' if 'FE_H_HOME_PTS_ROLL_FALLBACK' in df.columns else 'H_HOME_PTS_R3',
        'FE_A_AWAY_PTS_ROLL_FALLBACK' if 'FE_A_AWAY_PTS_ROLL_FALLBACK' in df.columns else 'A_AWAY_PTS_R3',
        'HOME_FTA_RATE_PRIOR',
        'AWAY_FTA_RATE_PRIOR',
        'REST_DIFF',
        'EXTREME_REST',
        'PACE_DIFF',
        'HOME_B2B_FLAG',
        'AWAY_B2B_FLAG',
        'HOME_EFG_PCT_FF_PRIOR',
        'AWAY_EFG_PCT_FF_PRIOR'
    ]
    # Keep only features that exist
    feature_cols = [c for c in feature_cols if c in df.columns]

    # Attach feature list to frame for convenience
    df.attrs['feature_cols'] = feature_cols

    return df


# ---------------------------
# Training & calibration
# ---------------------------
def train_and_calibrate(train_df, val_df, feature_cols, target_col='TARGET', base_model=None):
    X_train = train_df[feature_cols].values
    y_train = train_df[target_col].values
    X_val = val_df[feature_cols].values
    y_val = val_df[target_col].values

    if base_model is None:
        base_model = GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42)

    # Fit base model on train
    base_model.fit(X_train, y_train)

    # Calibrate on validation set (Platt scaling by default)
    calibrator = CalibratedClassifierCV(base_model, method='sigmoid', cv='prefit')
    calibrator.fit(X_val, y_val)

    return base_model, calibrator


# ---------------------------
# Evaluation utilities
# ---------------------------
def evaluate_model(model, calibrator, test_df, feature_cols, target_col='TARGET', plot=True):
    X_test = test_df[feature_cols].values
    y_test = test_df[target_col].values

    # raw preds and calibrated
    raw_proba = model.predict_proba(X_test)[:, 1]
    calib_proba = calibrator.predict_proba(X_test)[:, 1]

    preds = (calib_proba >= 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    ll = log_loss(y_test, calib_proba)
    auc = roc_auc_score(y_test, calib_proba)
    brier = brier_score_loss(y_test, calib_proba)

    print(f"Test Accuracy: {acc:.3f}")
    print(f"Test LogLoss: {ll:.4f}")
    print(f"Test ROC AUC:  {auc:.4f}")
    print(f"Test Brier:    {brier:.4f}")

    if plot:
        # Calibration curve
        prob_true, prob_pred = calibration_curve(y_test, calib_proba, n_bins=10)
        plt.figure(figsize=(6, 6))
        plt.plot(prob_pred, prob_true, marker='o', label='Calibrated')
        plt.plot([0, 1], [0, 1], linestyle='--', color='lightgray')
        plt.xlabel('Predicted probability')
        plt.ylabel('Observed fraction')
        plt.title('Calibration curve')
        plt.legend()
        plt.show()

        # Reliability by decile
        test_df = test_df.copy()
        test_df['_pred'] = calib_proba
        test_df['decile'] = pd.qcut(test_df['_pred'], 10, labels=False, duplicates='drop')
        dec = test_df.groupby('decile').agg(
            n=('TARGET', 'size'),
            mean_pred=('_pred', 'mean'),
            mean_actual=('TARGET', 'mean')
        ).reset_index()
        plt.figure(figsize=(10, 4))
        sns.barplot(data=dec, x='decile', y='mean_actual', palette="Blues_r")
        plt.plot(range(len(dec)), dec['mean_pred'], marker='o', color='orange', label='mean_pred')
        plt.title('Observed win rate by predicted-probability decile')
        plt.legend()
        plt.show()

    metrics = {
        'accuracy': acc,
        'logloss': ll,
        'roc_auc': auc,
        'brier': brier
    }
    return metrics


# ---------------------------
# Example workflow
# ---------------------------
if __name__ == "__main__":
    # Load
    df = pd.read_csv("data/processed/nba/final/nba_train_data_enhanced.csv", parse_dates=['GAME_DATE'])
    # Build features
    df_fe = build_prediction_features(df)
    feature_cols = df_fe.attrs.get('feature_cols', [c for c in df_fe.columns if c not in ['GAME_DATE','SEASON','TARGET','HOME_TEAM_ID','AWAY_TEAM_ID']])
    # Split
    train_df, val_df, test_df = temporal_split(df_fe)
    # Train & calibrate
    base_model, calibrator = train_and_calibrate(train_df, val_df, feature_cols)
    # Evaluate
    _ = evaluate_model(base_model, calibrator, test_df, feature_cols)
