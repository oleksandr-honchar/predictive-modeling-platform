import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, brier_score_loss
import seaborn as sns
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. Load + clean
# -------------------------------------------------
nba_file_path = 'C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\final\\nba_train_data_enhanced.csv'
nba_data = pd.read_csv(nba_file_path)
df = nba_data.dropna(axis=0).copy()

# -------------------------------------------------
# 2. Target + features
# -------------------------------------------------
y = df["HOME_WIN"].copy()

features = [
    'NET_RATING_DIFF',
    'HOME_NET_RATING_PRIOR',
    'AWAY_NET_RATING_PRIOR',
    'HOME_B2B',
    'AWAY_B2B',
    'REST_ADVANTAGE'
]

X = df[features].copy()

# -------------------------------------------------
# 3. Chronological split
# -------------------------------------------------
split_idx = int(0.75 * len(df))
train_df = df.iloc[:split_idx].copy()
val_df   = df.iloc[split_idx:].copy()

train_X = X.iloc[:split_idx]
train_y = y.iloc[:split_idx]
val_X   = X.iloc[split_idx:]
val_y   = y.iloc[split_idx:]

# -------------------------------------------------
# 4. Brier Skill Score
# -------------------------------------------------
def brier_skill_score(y_true, y_pred_proba, baseline_prob):
    bs_model = brier_score_loss(y_true, y_pred_proba)
    baseline_preds = np.full_like(y_pred_proba, baseline_prob)
    bs_baseline = brier_score_loss(y_true, baseline_preds)
    bss = 1 - (bs_model / bs_baseline)

    print(f"Model Brier Score: {bs_model:.4f}")
    print(f"Baseline Brier Score: {bs_baseline:.4f}")
    print(f"Brier Skill Score: {bss:.4f}")

    if bss > 0.15:
        print("→ Excellent improvement over baseline")
    elif bss > 0.08:
        print("→ Good improvement over baseline")
    elif bss > 0:
        print("→ Modest improvement over baseline")
    else:
        print("→ WARNING: Model worse than baseline!")

    return bss

# -------------------------------------------------
# 5. Decision tree evaluation
# -------------------------------------------------
def get_accuracy(max_leaf_nodes, train_X, val_X, train_y, val_y):
    model = DecisionTreeClassifier(max_leaf_nodes=max_leaf_nodes, random_state=0)
    model.fit(train_X, train_y)
    preds = model.predict(val_X)
    proba = model.predict_proba(val_X)[:, 1]
    return accuracy_score(val_y, preds), proba

print("Max leaf nodes → Accuracy | Brier Score")
results = {}
for max_leaf_nodes in [3, 4, 5, 6]:
    acc, proba = get_accuracy(max_leaf_nodes, train_X, val_X, train_y, val_y)
    brier = brier_score_loss(val_y, proba)
    results[max_leaf_nodes] = (acc, brier)
    print(f"{max_leaf_nodes:>3} → {acc:.4f} | Brier: {brier:.4f}")

# -------------------------------------------------
# 6. Brier decomposition (for chosen tree size)
# -------------------------------------------------
def brier_decomposition(y_true, y_pred_proba):
    df_temp = pd.DataFrame({'y': y_true, 'p': y_pred_proba})
    df_temp['bin'] = pd.qcut(df_temp['p'], q=10, duplicates='drop')

    grouped = df_temp.groupby('bin').agg(
        mean_p=('p', 'mean'),
        mean_y=('y', 'mean'),
        count=('y', 'size')
    )

    reliability = np.sum(grouped['count'] * (grouped['mean_p'] - grouped['mean_y'])**2) / len(df_temp)
    resolution  = np.sum(grouped['count'] * (grouped['mean_y'] - y_true.mean())**2) / len(df_temp)
    uncertainty = y_true.mean() * (1 - y_true.mean())

    bs = brier_score_loss(y_true, y_pred_proba)

    print("\n--- Brier Score Decomposition ---")
    print(f"Brier Score: {bs:.4f}")
    print(f"  Reliability: {reliability:.4f}")
    print(f"  Resolution:  {resolution:.4f}")
    print(f"  Uncertainty: {uncertainty:.4f}")
    print(f"Verification: {bs:.4f}")

    return reliability, resolution, uncertainty

# Run decomposition on best-performing tree (example: max_leaf_nodes=4)
max_leaf_best = 4
_, y_pred_proba = get_accuracy(max_leaf_best, train_X, val_X, train_y, val_y)
brier_decomposition(val_y, y_pred_proba)

# -------------------------------------------------
# 7. Brier Skill Score using home win rate baseline
# -------------------------------------------------
home_win_rate = train_y.mean()
print(f"\nHome win baseline rate = {home_win_rate:.4f}")

bss = brier_skill_score(val_y, y_pred_proba, baseline_prob=home_win_rate)

# -------------------------------------------------
# 8. Feature importance plot
# -------------------------------------------------
sns.set(style="darkgrid")
plt.style.use("dark_background")

final_model = DecisionTreeClassifier(max_leaf_nodes=500, random_state=0)
final_model.fit(train_X, train_y)

importances = pd.Series(final_model.feature_importances_, index=features)
importances = importances.sort_values(ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(x=importances.values, y=importances.index, palette="Blues_r")
plt.title("Feature Importance – Decision Tree (Dark Mode)")
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.show()

# -------------------------------------------------
# 9. Model upgrade chain (Net Rating → Four Factors → Full)
# -------------------------------------------------
from xgboost import XGBClassifier

params = dict(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.9,
    colsample_bytree=0.9,
    objective='binary:logistic',
    eval_metric='logloss'
)

# --- Baseline: net rating only
features_baseline = ['NET_RATING_DIFF']
X_train_base = train_df[features_baseline]
X_val_base   = val_df[features_baseline]

model_base = XGBClassifier(**params)
model_base.fit(X_train_base, train_y)
preds_base = model_base.predict_proba(X_val_base)[:, 1]
brier_base = brier_score_loss(val_y, preds_base)
print(f"\nBaseline (Net Rating only): {brier_base:.4f}")

# --- Four factors
features_four_factors = [
    'NET_RATING_DIFF',
    'EFG_PCT_DIFF',
    'TOV_PCT_DIFF',
    'OREB_PCT_DIFF',
    'FTA_RATE_DIFF'
]

X_train_ff = train_df[features_four_factors]
X_val_ff   = val_df[features_four_factors]

model_ff = XGBClassifier(**params)
model_ff.fit(X_train_ff, train_y)
preds_ff = model_ff.predict_proba(X_val_ff)[:, 1]
brier_ff = brier_score_loss(val_y, preds_ff)

print(f"With Four Factors: {brier_ff:.4f}")
print(f"Improvement: {brier_base - brier_ff:.4f}")

# --- Full model with rest/schedule
features_full = features_four_factors + [
    'REST_ADVANTAGE',
    'HOME_B2B',
    'AWAY_B2B'
]

X_train_full = train_df[features_full]
X_val_full   = val_df[features_full]

model_full = XGBClassifier(**params)
model_full.fit(X_train_full, train_y)
preds_full = model_full.predict_proba(X_val_full)[:, 1]
brier_full = brier_score_loss(val_y, preds_full)

print(f"With Rest Features: {brier_full:.4f}")
print(f"Improvement: {brier_ff - brier_full:.4f}")