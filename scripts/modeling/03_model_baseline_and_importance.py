"""
Model Training + Optuna Hyperparameter Optimization
===================================================

Trains 3 models:
1. Logistic Regression (baseline)
2. Random Forest
3. HistGradientBoostingClassifier

Outputs:
- Best hyperparameters
- Best CV scores
- Feature importance charts
- Comparison leaderboard

Requires: optuna, sklearn, seaborn, matplotlib
"""

import pandas as pd
import numpy as np
import optuna
from optuna.samplers import TPESampler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style="darkgrid")
plt.style.use("dark_background")


# ======================================================================
# LOAD DATA
# ======================================================================

DATA_FILE = "data/processed/nba/final/nba_train_data.csv"
df = pd.read_csv(DATA_FILE)

TARGET = "HOME_WIN"

# Drop IDs + date columns
drop_cols = [c for c in df.columns if "TEAM_ID" in c or "DATE" in c or "NAME" in c]
df = df.drop(columns=drop_cols)

# Clean NaN
df = df.fillna(0)

X = df.drop(columns=[TARGET])
y = df[TARGET]

numeric_features = list(X.columns)

# detect columns automatically
numeric_features = X.select_dtypes(include=["int64", "float64"]).columns
categorical_features = X.select_dtypes(include=["object"]).columns

preprocess = ColumnTransformer([
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
])


# ======================================================================
# OPTUNA OBJECTIVES
# ======================================================================

def objective_logreg(trial):
    C = trial.suggest_float("C", 0.001, 10.0, log=True)
    penalty = "l2"

    clf = Pipeline([
        ("prep", preprocess),
        ("model", LogisticRegression(C=C, penalty=penalty, max_iter=10_000))
    ])

    score = cross_val_score(clf, X, y, cv=4, scoring="accuracy").mean()
    return score


def objective_rf(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 600),
        "max_depth": trial.suggest_int("max_depth", 3, 40),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
        "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
    }

    clf = Pipeline([
        ("prep", preprocess),
        ("model", RandomForestClassifier(**params))
    ])

    score = cross_val_score(clf, X, y, cv=4, scoring="accuracy").mean()
    return score


def objective_hgb(trial):
    params = {
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.5, log=True),
        "max_depth": trial.suggest_int("max_depth", 2, 40),
        "max_leaf_nodes": trial.suggest_int("max_leaf_nodes", 5, 80),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 10, 80),
    }

    clf = Pipeline([
        ("prep", preprocess),
        ("model", HistGradientBoostingClassifier(**params))
    ])

    score = cross_val_score(clf, X, y, cv=4, scoring="accuracy").mean()
    return score


# ======================================================================
# RUN OPTUNA TUNING
# ======================================================================

def run_study(name, objective, n_trials=35):
    print("\n" + "=" * 80)
    print(f"  OPTIMIZING: {name}")
    print("=" * 80)

    study = optuna.create_study(
        direction="maximize",
        sampler=TPESampler(seed=42)
    )
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

    print("\nBest Score:", study.best_value)
    print("Best Params:", study.best_params)
    return study


study_lr = run_study("Logistic Regression", objective_logreg)
study_rf = run_study("Random Forest", objective_rf)
study_hgb = run_study("HistGradientBoosting", objective_hgb)


# ======================================================================
# REFIT FINAL MODELS WITH BEST PARAMS
# ======================================================================

def fit_best(study, model_type):
    params = study.best_params

    if model_type == "lr":
        model = LogisticRegression(C=params["C"], max_iter=10_000)

    elif model_type == "rf":
        model = RandomForestClassifier(**params)

    elif model_type == "hgb":
        model = HistGradientBoostingClassifier(**params)

    pipe = Pipeline([
        ("prep", preprocess),
        ("model", model)
    ])
    pipe.fit(X, y)
    return pipe


model_lr = fit_best(study_lr, "lr")
model_rf = fit_best(study_rf, "rf")
model_hgb = fit_best(study_hgb, "hgb")


# ======================================================================
# FEATURE IMPORTANCE
# ======================================================================

def plot_importance(model, model_name):
    if hasattr(model.named_steps["model"], "feature_importances_"):
        importances = model.named_steps["model"].feature_importances_
    else:
        print(f"No importance available for {model_name}")
        return

    imp_df = pd.DataFrame({
        "feature": numeric_features,
        "importance": importances
    }).sort_values("importance", ascending=False)

    plt.figure(figsize=(10, 8))
    sns.barplot(
        data=imp_df.head(25),
        y="feature",
        x="importance",
        palette="Blues_r"
    )
    plt.title(f"{model_name} — Top 25 Feature Importances")
    plt.tight_layout()
    plt.show()

plot_importance(model_rf, "Random Forest")
plot_importance(model_hgb, "HistGradientBoosting")


# ======================================================================
# LEADERBOARD
# ======================================================================

print("\n\n====================== MODEL LEADERBOARD ======================")
leaderboard = pd.DataFrame({
    "Model": ["LogReg", "RandomForest", "HistGB"],
    "CV Score": [
        study_lr.best_value,
        study_rf.best_value,
        study_hgb.best_value
    ]
})
print(leaderboard.sort_values("CV Score", ascending=False))
print("===============================================================")
