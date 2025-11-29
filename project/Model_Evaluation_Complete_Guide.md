# Model Evaluation - Complete Study Guide
**Date:** November 27, 2025  
**Duration:** 4 hours afternoon session  
**Topics:** Train/Test Splits, Cross-Validation, Calibration, Brier Score, Kelly Criterion, ROI

---

## Table of Contents
1. [Train/Test Splits](#train-test-splits)
2. [Cross-Validation](#cross-validation)
3. [Calibration](#calibration)
4. [Brier Score](#brier-score)
5. [Kelly Criterion](#kelly-criterion)
6. [ROI Calculation](#roi-calculation)
7. [Implementation Checklist](#implementation-checklist)

---

## Train/Test Splits

### Purpose
Simulate real-world performance where the model makes predictions on unseen data.

### Your Current Setup (CORRECT ✅)
- **Training Set (70%)**: (earliest)
- **Validation Set (15%)**: (middle)
- **Test Set (15%)**: (most recent)
- **Split method**: Chronological (respects temporal ordering)

### Why Chronological Splitting?
1. No future information leaks into past
2. Realistic evaluation (test set = actual prediction scenario)
3. Matches how sportsbooks operate

### Critical Rule
**For a game on January 15, use stats calculated through January 14**

Use `_PRIOR` columns exclusively for features to ensure temporal integrity.

### Verification Code
```python
# Verify no data leakage
assert all('PRIOR' in col or col in ['GAME_ID', 'HOME_WIN', 'REST_ADVANTAGE', etc.] 
           for col in feature_cols if col not in target_cols)

# Check chronological ordering
assert train_df['GAME_DATE'].max() < val_df['GAME_DATE'].min()
assert val_df['GAME_DATE'].max() < test_df['GAME_DATE'].min()

# Verify no duplicate games
assert len(set(train_df['GAME_ID']) & set(val_df['GAME_ID'])) == 0
```

### Red Flags
- Train accuracy 75%, validation 62% → Overfitting
- Validation log loss 0.55, test log loss 0.75 → Not generalizing
- Train/val similar, test very different → Distribution shift

---

## Cross-Validation

### Standard K-Fold (NOT for Time-Series)
❌ Breaks temporal ordering - trains on future to predict past

### Time-Series Cross-Validation (Your Option)

#### Expanding Window CV (Recommended)
```
Fold 1: Train [Games 1-1000]     → Validate [Games 1001-1500]
Fold 2: Train [Games 1-1500]     → Validate [Games 1501-2000]
Fold 3: Train [Games 1-2000]     → Validate [Games 2001-2500]
Fold 4: Train [Games 1-2500]     → Validate [Games 2501-3000]
Fold 5: Train [Games 1-3000]     → Validate [Games 3001-3500]
```

#### Implementation
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)

cv_scores = {
    'accuracy': [],
    'log_loss': [],
    'brier_score': []
}

for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    
    model = XGBClassifier(**params)
    model.fit(X_train, y_train)
    
    y_pred_proba = model.predict_proba(X_val)[:, 1]
    
    cv_scores['accuracy'].append(accuracy_score(y_val, (y_pred_proba > 0.5).astype(int)))
    cv_scores['log_loss'].append(log_loss(y_val, y_pred_proba))
    cv_scores['brier_score'].append(brier_score_loss(y_val, y_pred_proba))

print(f"CV Accuracy: {np.mean(cv_scores['accuracy']):.3f} ± {np.std(cv_scores['accuracy']):.3f}")
```

### Recommendation for Your Project
- **Week 2-3**: Use simple holdout (fast iteration)
- **Week 4-5**: Run time-series CV for final validation and confidence intervals

---

## Calibration

### Definition
Calibration measures whether predicted probabilities match reality.

**Perfect calibration:** When model says "70% chance," team wins 70% of the time.

### Why Critical for Betting Models
1. **Trust**: Users need honest probabilities
2. **Kelly Criterion**: Optimal bet sizing requires accurate probabilities
3. **Educational value**: Transparency mission depends on truthful predictions
4. **Long-term viability**: Miscalibrated models destroy bankrolls

### Calibration Curve
```python
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

y_pred_proba = model.predict_proba(X_val)[:, 1]
prob_true, prob_pred = calibration_curve(y_val, y_pred_proba, n_bins=10)

plt.figure(figsize=(10, 6))
plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
plt.plot(prob_pred, prob_true, 'o-', label='Model Calibration')
plt.xlabel('Predicted Probability')
plt.ylabel('Observed Frequency')
plt.title('Calibration Curve')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

### Interpreting Curves
- **On diagonal**: Perfect calibration
- **Below diagonal**: Overconfident (model says 80%, actual 65%)
- **Above diagonal**: Underconfident (model says 60%, actual 67%)

### Expected Calibration Error (ECE)
```python
def expected_calibration_error(y_true, y_pred_proba, n_bins=10):
    prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=n_bins)
    
    bins = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(y_pred_proba, bins) - 1
    
    ece = 0
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.sum() > 0:
            bin_acc = y_true[mask].mean()
            bin_conf = y_pred_proba[mask].mean()
            bin_size = mask.sum() / len(y_true)
            ece += bin_size * abs(bin_acc - bin_conf)
    
    return ece
```

**Benchmarks:**
- ECE < 0.05: Excellent calibration
- ECE 0.05-0.10: Good calibration
- ECE 0.10-0.15: Moderate miscalibration
- ECE > 0.15: Poor calibration, needs fixing

### Fixing Miscalibration: Platt Scaling
```python
from sklearn.calibration import CalibratedClassifierCV

# Train base model
base_model = XGBClassifier(**params)
base_model.fit(X_train, y_train)

# Apply Platt scaling
calibrated_model = CalibratedClassifierCV(
    base_model, 
    method='sigmoid',  # Platt scaling
    cv='prefit'
)
calibrated_model.fit(X_val, y_val)

# Get calibrated predictions
test_preds_calibrated = calibrated_model.predict_proba(X_test)[:, 1]
```

**When to use:**
- XGBoost models (common scenario - they tend to be overconfident)
- ECE > 0.05
- Have 200+ validation samples

---

## Brier Score

### Definition
Mean squared error of probability predictions. Measures both calibration AND discrimination.

**Formula:**
```
Brier Score = (1/N) × Σ(predicted_probability - actual_outcome)²
```

**Range:** 0 (perfect) to 1 (worst)  
**Lower is better**

### Benchmarks for NBA

| Brier Score | Quality | Notes |
|-------------|---------|-------|
| < 0.15 | Exceptional | Top-tier professional |
| 0.15-0.18 | Excellent | Advanced analytics |
| 0.18-0.20 | Very Good | Solid predictive model |
| 0.20-0.23 | Good | Simple models |
| 0.25 | Baseline | Always predict 50% |

**Your target:** < 0.20 (very good)

### Implementation
```python
from sklearn.metrics import brier_score_loss

brier = brier_score_loss(y_val, y_pred_proba)
print(f"Brier Score: {brier:.4f}")
```

### Brier Score Decomposition
```
Brier Score = Reliability - Resolution + Uncertainty
```

- **Reliability (↓ better)**: Calibration component
- **Resolution (↑ better)**: Discrimination component
- **Uncertainty (fixed)**: Inherent randomness (~0.20-0.22 for basketball)

### Brier Skill Score (BSS)
```python
def brier_skill_score(y_true, y_pred_proba, baseline_prob=0.5):
    bs_model = brier_score_loss(y_true, y_pred_proba)
    baseline_preds = np.full_like(y_pred_proba, baseline_prob)
    bs_baseline = brier_score_loss(y_true, baseline_preds)
    
    bss = 1 - (bs_model / bs_baseline)
    return bss
```

**Benchmarks:**
- BSS > 0.20: Excellent
- BSS 0.10-0.20: Very good
- BSS 0.05-0.10: Good
- BSS < 0.05: Marginal

---

## Kelly Criterion

### Purpose
Determines optimal bet size to maximize long-term bankroll growth.

### The Formula
```
Kelly % = (bp - q) / b

Where:
- b = decimal odds - 1 (profit per unit staked)
- p = probability of winning (your model)
- q = probability of losing = 1 - p
```

### Implementation
```python
def kelly_criterion(model_prob, american_odds):
    # Convert to decimal odds
    if american_odds < 0:
        decimal_odds = 1 + (100 / abs(american_odds))
    else:
        decimal_odds = 1 + (american_odds / 100)
    
    # Net odds (profit per unit)
    b = decimal_odds - 1
    
    # Probabilities
    p = model_prob
    q = 1 - p
    
    # Kelly formula
    kelly = (b * p - q) / b
    
    # Don't bet if kelly is negative
    kelly = max(0, kelly)
    
    return kelly
```

### Fractional Kelly (RECOMMENDED)
```python
def fractional_kelly(model_prob, american_odds, fraction=0.25):
    full_kelly = kelly_criterion(model_prob, american_odds)
    return full_kelly * fraction
```

**Common fractions:**
- **1/4 Kelly (0.25)**: Conservative, recommended for most ✅
- **1/2 Kelly (0.50)**: Moderate
- **Full Kelly (1.0)**: Aggressive, high variance

### Why Fractional Kelly?
1. Accounts for model uncertainty
2. Reduces variance and drawdowns
3. Protects against miscalibration
4. Industry standard (professionals use 1/4 to 1/2 Kelly)

### Betting Thresholds
```python
def should_bet(model_prob, market_odds, min_edge=0.03, min_kelly=0.02):
    market_prob = american_odds_to_probability(market_odds)
    edge = model_prob - market_prob
    kelly = kelly_criterion(model_prob, market_odds)
    
    if edge < min_edge:
        return False, f"Edge too small: {edge*100:.2f}%"
    
    if kelly < min_kelly:
        return False, f"Kelly too small: {kelly*100:.2f}%"
    
    return True, f"✅ Bet: Edge {edge*100:.1f}%, Kelly {kelly*100:.1f}%"
```

---

## ROI Calculation

### Definition
```
ROI = (Total Profit / Total Amount Wagered) × 100%
```

### Implementation
```python
def calculate_roi(bets_df):
    total_staked = bets_df['stake'].sum()
    
    profits = []
    for _, bet in bets_df.iterrows():
        if bet['result'] == 1:  # Win
            if bet['odds'] < 0:
                profit = bet['stake'] * (100 / abs(bet['odds']))
            else:
                profit = bet['stake'] * (bet['odds'] / 100)
        else:  # Loss
            profit = -bet['stake']
        profits.append(profit)
    
    total_profit = sum(profits)
    roi = (total_profit / total_staked) * 100
    
    return {
        'total_staked': total_staked,
        'total_profit': total_profit,
        'roi': roi,
        'win_rate': bets_df['result'].mean()
    }
```

### ROI Benchmarks

| ROI | Quality | Notes |
|-----|---------|-------|
| > 10% | Exceptional | Elite professional level |
| 5-10% | Excellent | Sustainable edge |
| 2-5% | Good | Profitable, competitive |
| 0-2% | Marginal | Barely profitable |
| < 0% | Losing | Need improvement |

**Your target for NBA:** 3-4% ROI (realistic and profitable)

### Expected Value (EV)
```python
def calculate_ev(model_prob, odds, stake=100):
    # Convert odds to profit multiplier
    if odds < 0:
        profit_multiplier = 100 / abs(odds)
    else:
        profit_multiplier = odds / 100
    
    profit_if_win = stake * profit_multiplier
    loss_if_lose = stake
    
    ev = (model_prob * profit_if_win) - ((1 - model_prob) * loss_if_lose)
    
    return ev
```

**Betting rule:** Only bet when EV > 0

---

## Implementation Checklist

### Phase 1: Model Training & Evaluation
- [ ] Train XGBoost on training set with `_PRIOR` features only
- [ ] Evaluate on validation set (accuracy, log loss, Brier score)
- [ ] Generate calibration curve
- [ ] Calculate ECE (target: < 0.10)
- [ ] Apply Platt scaling if ECE > 0.05
- [ ] Re-evaluate calibrated model

### Phase 2: Robust Validation
- [ ] Run 5-fold time-series cross-validation
- [ ] Calculate mean ± std for all metrics
- [ ] Document confidence intervals
- [ ] Check for performance degradation over time

### Phase 3: Test Set Evaluation (ONCE ONLY)
- [ ] Load test set
- [ ] Generate predictions with calibrated model
- [ ] Calculate all metrics (accuracy, log loss, Brier, ECE)
- [ ] Generate final calibration curve
- [ ] Document results

### Phase 4: Betting Integration
- [ ] Integrate odds API (The Odds API)
- [ ] Implement Kelly Criterion calculator
- [ ] Set betting thresholds (min edge 3%, min Kelly 2%)
- [ ] Simulate historical betting performance
- [ ] Calculate ROI on historical data

### Phase 5: Production Monitoring
- [ ] Track calibration weekly
- [ ] Monitor rolling Brier score (50-game window)
- [ ] Calculate running ROI
- [ ] Alert if ECE > 0.15 (recalibration needed)
- [ ] Update calibration curves on website

---

## Your Target Metrics (Summary)

| Metric | Minimum | Target | Stretch |
|--------|---------|--------|---------|
| **Accuracy** | 62% | 68% | 72% |
| **Log Loss** | < 0.65 | < 0.60 | < 0.55 |
| **Brier Score** | < 0.23 | < 0.20 | < 0.18 |
| **ECE** | < 0.15 | < 0.10 | < 0.05 |
| **Brier Skill Score** | > 0.08 | > 0.15 | > 0.20 |
| **ROI** | > 0% | 3-4% | 5-8% |

---

## Key Takeaways

1. **Temporal Integrity is Sacred**: Always use `_PRIOR` features, chronological splits
2. **Calibration > Pure Accuracy**: Honest probabilities build trust
3. **Brier Score is Your North Star**: Combines calibration and discrimination
4. **Use Fractional Kelly**: 1/4 Kelly protects against model uncertainty
5. **Set Realistic Expectations**: 3-4% ROI is excellent in sports betting
6. **Monitor Continuously**: Track calibration and performance over time

---

## Next Steps

Tomorrow (November 28):
1. Continue Intermediate ML course (Pipelines, Cross-Validation)
2. Begin feature planning and prioritization
3. Design feature engineering pipeline (rolling averages, rest days, H2H)
4. Apply today's evaluation concepts to actual model training

---

**Session completed:** November 27, 2025, 6:00 PM  
**Confidence level:** High ✅  
**Ready for model training:** Yes