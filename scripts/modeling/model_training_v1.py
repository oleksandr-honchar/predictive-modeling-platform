import pandas as pd
from datetime import datetime
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
from xgboost import XGBClassifier

# ----------------------------------------------------------------------------
# Data Loading & Splitting
# ----------------------------------------------------------------------------
def load_and_split_data(csv_path="C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\nba_train_data.csv"):
    df = pd.read_csv(csv_path)
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df = df.sort_values("GAME_DATE").reset_index(drop=True)

    total = len(df)
    val_idx = int(total * 0.70)
    test_idx = int(total * 0.85)

    train_df = df.iloc[:val_idx].copy()
    val_df = df.iloc[val_idx:test_idx].copy()
    test_df = df.iloc[test_idx:].copy()

    X_train, y_train = extract_features(train_df)
    X_val, y_val = extract_features(val_df)
    X_test, y_test = extract_features(test_df)

    return X_train, y_train, X_val, y_val, X_test, y_test, train_df, val_df, test_df


# ----------------------------------------------------------------------------
# Feature Extraction
# ----------------------------------------------------------------------------
def extract_features(df):
    metadata = [
        "GAME_ID", "GAME_DATE", "SEASON",
        "HOME_TEAM_ID", "HOME_TEAM_ABBREVIATION", "HOME_TEAM_NAME",
        "AWAY_TEAM_ID", "AWAY_TEAM_ABBREVIATION", "AWAY_TEAM_NAME",
        "HOME_WL", "AWAY_WL",
    ]

    results = [
        "HOME_PTS", "AWAY_PTS", "HOME_PLUS_MINUS", "AWAY_PLUS_MINUS",
        "HOME_FGM", "HOME_FGA", "HOME_FG_PCT", "HOME_FG3M", "HOME_FG3A", "HOME_FG3_PCT",
        "HOME_FTM", "HOME_FTA", "HOME_FT_PCT", "HOME_OREB", "HOME_DREB", "HOME_REB",
        "HOME_AST", "HOME_STL", "HOME_BLK", "HOME_TOV", "HOME_PF",
        "AWAY_FGM", "AWAY_FGA", "AWAY_FG_PCT", "AWAY_FG3M", "AWAY_FG3A", "AWAY_FG3_PCT",
        "AWAY_FTM", "AWAY_FTA", "AWAY_FT_PCT", "AWAY_OREB", "AWAY_DREB", "AWAY_REB",
        "AWAY_AST", "AWAY_STL", "AWAY_BLK", "AWAY_TOV", "AWAY_PF",
    ]

    season_stats = [
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

    exclude = metadata + results + season_stats + ["HOME_WIN"]
    exclude = [c for c in exclude if c in df.columns]

    X = df.drop(columns=exclude)
    y = df["HOME_WIN"]

    return X, y


# ----------------------------------------------------------------------------
# Evaluation
# ----------------------------------------------------------------------------
def evaluate(model, X, y):
    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1]

    acc = accuracy_score(y, pred)
    ll = log_loss(y, proba)
    auc = roc_auc_score(y, proba)

    return acc, ll, auc


# ----------------------------------------------------------------------------
# Calibration Plot
# ----------------------------------------------------------------------------
def plot_calibration(y_true, y_pred_proba, n_bins=10, save_path=None):
    prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=n_bins)

    plt.figure(figsize=(8, 6))
    plt.plot(prob_pred, prob_true, marker="o")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("Predicted Probability")
    plt.ylabel("Actual Win Rate")
    plt.title("Calibration Curve")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


# ----------------------------------------------------------------------------
# Main Execution
# ----------------------------------------------------------------------------
def main():
    X_train, y_train, X_val, y_val, X_test, y_test, train_df, val_df, test_df = load_and_split_data()

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

    model.fit(X_train, y_train)

    val_acc, val_ll, val_auc = evaluate(model, X_val, y_val)
    print(f"Validation → Acc: {val_acc:.3f}, LogLoss: {val_ll:.3f}, AUC: {val_auc:.3f}")

    test_acc, test_ll, test_auc = evaluate(model, X_test, y_test)
    print(f"Test → Acc: {test_acc:.3f}, LogLoss: {test_ll:.3f}, AUC: {test_auc:.3f}")

    proba_test = model.predict_proba(X_test)[:, 1]
    plot_calibration(y_test, proba_test, save_path="calibration.png")


if __name__ == "__main__":
    main()
