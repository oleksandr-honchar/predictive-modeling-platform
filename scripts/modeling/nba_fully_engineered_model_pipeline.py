import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit, cross_validate, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss, make_scorer
from xgboost import XGBClassifier
import os

# =====================================================================
# CONFIG
# =====================================================================

DATA_PATH = r"C:\Users\userPC\projects\predictive-modeling-platform\data\processed\nba\final\nba_train_data_fully_engineered.csv"
TARGET = "HOME_WIN"
N_SPLITS = 5
RANDOM_STATE = 42

# =====================================================================
# FEATURE SETS (match engineered pipeline)
# =====================================================================

FEATURES_BASELINE = ["NET_RATING_DIFF"]

FEATURES_FOUR_FACTORS = [
    "NET_RATING_DIFF", "EFG_PCT_FF_L5_DIFF", "TOV_PCT_L5_DIFF",
    "OREB_PCT_FF_L5_DIFF", "FTA_RATE_L5_DIFF"
]
FEATURES_ROLLING = [
    "NET_RATING_L5_DIFF", "NET_RATING_L10_DIFF",
    "W_PCT_L5_DIFF", "EFG_PCT_FF_L5_DIFF"
]
FEATURES_MOMENTUM = ["MOMENTUM", "WIN_STREAK"]

FEATURES_REST = [
    "REST_ADVANTAGE",
    "HOME_B2B", "AWAY_B2B",
    "HOME_SEASON_PROGRESS", "AWAY_SEASON_PROGRESS",
    "B2B_IN_L5_HOME", "B2B_IN_L5_AWAY",
    "B2B_IN_L10_HOME", "B2B_IN_L10_AWAY",
    "AVG_REST_L10_HOME", "AVG_REST_L10_AWAY",
    "OPTIMAL_REST_HOME", "OPTIMAL_REST_AWAY",
    "OVER_RESTED_HOME", "OVER_RESTED_AWAY"
]

FEATURES_H2H = [
    "H2H_HOME_WIN_PCT", "H2H_HOME_WINS", "H2H_GAMES"
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

# =====================================================================
# LOAD DATA
# =====================================================================

def load_data(path):
    df = pd.read_csv(path)
    if "GAME_DATE" in df.columns:
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
        df = df.sort_values("GAME_DATE").reset_index(drop=True)
    df = df.dropna(subset=[TARGET])
    return df

# =====================================================================
# PIPELINES
# =====================================================================

def preprocessing():
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

def make_pipeline(model, scale=False):
    if scale:
        return Pipeline([("preprocess", preprocessing()), ("clf", model)])
    else:
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("clf", model)])

# =====================================================================
# CROSS-VALIDATION
# =====================================================================

def evaluate_cv(pipeline, X, y):
    scoring = {
        "accuracy": "accuracy",
        "log_loss": "neg_log_loss",
        "brier": make_scorer(brier_score_loss, needs_proba=True, greater_is_better=False)
    }
    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    results = cross_validate(pipeline, X, y, cv=tscv, scoring=scoring, n_jobs=-1, return_train_score=False)
    return {
        "accuracy": -results["test_accuracy"].mean(),
        "log_loss": -results["test_log_loss"].mean(),
        "brier": -results["test_brier"].mean()
    }

# =====================================================================
# MODEL COMPARISON
# =====================================================================

def compare_models(df):
    y = df[TARGET]
    results = []
    for name, feats in FEATURE_SETS.items():
        feats = [f for f in feats if f in df.columns]
        if not feats:
            continue
        X = df[feats]

        # Decision Tree
        dt = make_pipeline(DecisionTreeClassifier(max_depth=5, random_state=RANDOM_STATE))
        dt_res = evaluate_cv(dt, X, y)
        results.append({"Feature Set": name, "Model": "Decision Tree", **dt_res})

        # XGBoost
        xgb = make_pipeline(XGBClassifier(
            n_estimators=120,
            learning_rate=0.08,
            max_depth=4,
            eval_metric="logloss",
            random_state=RANDOM_STATE
        ))
        xgb_res = evaluate_cv(xgb, X, y)
        results.append({"Feature Set": name, "Model": "XGBoost", **xgb_res})

    return pd.DataFrame(results)

# =====================================================================
# GRID SEARCH
# =====================================================================

def tune_xgb(X, y):
    base = make_pipeline(XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE))
    param_grid = {
        "clf__max_depth": [3, 4, 5],
        "clf__learning_rate": [0.05, 0.1],
        "clf__n_estimators": [100, 200]
    }
    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    gs = GridSearchCV(base, param_grid, cv=tscv, scoring="neg_log_loss", n_jobs=-1, verbose=1)
    gs.fit(X, y)
    return gs

# =====================================================================
# FINAL EVALUATION
# =====================================================================

def evaluate_final(model, X_train, y_train, X_val, y_val, X_test, y_test):
    model.fit(X_train, y_train)
    def score(X, y):
        proba = model.predict_proba(X)[:, 1]
        return {"accuracy": accuracy_score(y, proba > 0.5), "log_loss": log_loss(y, proba),
                "brier": brier_score_loss(y, proba), "proba": proba}
    val = score(X_val, y_val)
    test = score(X_test, y_test)
    baseline = y_train.mean()
    bss = 1 - (test["brier"] / brier_score_loss(y_test, np.full_like(test["proba"], baseline)))
    test["baseline"] = baseline
    test["brier_skill"] = bss
    return val, test

# =====================================================================
# MAIN
# =====================================================================

def main():
    df = load_data(DATA_PATH)

    # Model comparison
    comp = compare_models(df)
    print("\nMODEL COMPARISON:\n", comp)

    # Hyperparameter tuning
    X_full = [f for f in FEATURES_ENGINEERED if f in df.columns]
    y = df[TARGET]
    gs = tune_xgb(df[X_full], y)
    best = gs.best_estimator_

    # Train/val/test split
    n = len(df)
    i1, i2 = int(n * 0.70), int(n * 0.85)
    train, val, test = df.iloc[:i1], df.iloc[i1:i2], df.iloc[i2:]

    X_train, X_val, X_test = train[X_full], val[X_full], test[X_full]
    y_train, y_val, y_test = train[TARGET], val[TARGET], test[TARGET]

    val_res, test_res = evaluate_final(best, X_train, y_train, X_val, y_val, X_test, y_test)
    print("\nVAL RESULTS:", val_res)
    print("\nTEST RESULTS:", test_res)

    return comp, gs, val_res, test_res

if __name__ == "__main__":
    main()
