"""
Model Evaluation Functions - Reference Implementation
Date: November 27, 2025
Purpose: Essential functions for NBA prediction model evaluation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, log_loss, brier_score_loss, 
    roc_auc_score, confusion_matrix
)
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.model_selection import TimeSeriesSplit


# ============================================
# CALIBRATION FUNCTIONS
# ============================================

def expected_calibration_error(y_true, y_pred_proba, n_bins=10):
    """
    Calculate Expected Calibration Error (ECE)
    
    Args:
        y_true: True labels (0 or 1)
        y_pred_proba: Predicted probabilities
        n_bins: Number of bins for calibration
    
    Returns:
        ECE value (lower is better)
        
    Benchmarks:
        < 0.05: Excellent
        0.05-0.10: Good
        0.10-0.15: Moderate
        > 0.15: Poor (needs calibration)
    """
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


def plot_calibration_curve(y_true, y_pred_proba, model_name="Model", n_bins=10):
    """
    Plot calibration curve with ECE
    """
    prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=n_bins)
    ece = expected_calibration_error(y_true, y_pred_proba, n_bins=n_bins)
    
    plt.figure(figsize=(10, 6))
    plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration', linewidth=2)
    plt.plot(prob_pred, prob_true, 'o-', label=f'{model_name} (ECE={ece:.4f})', 
             markersize=8, linewidth=2)
    plt.xlabel('Predicted Probability', fontsize=12)
    plt.ylabel('Observed Frequency', fontsize=12)
    plt.title('Calibration Curve', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def apply_platt_scaling(base_model, X_train, y_train, X_val, y_val):
    """
    Apply Platt scaling to calibrate model
    
    Args:
        base_model: Trained sklearn model
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
    
    Returns:
        calibrated_model: Calibrated model ready for predictions
    """
    # Train base model if not already trained
    if not hasattr(base_model, 'classes_'):
        base_model.fit(X_train, y_train)
    
    # Apply Platt scaling
    calibrated_model = CalibratedClassifierCV(
        base_model,
        method='sigmoid',
        cv='prefit'
    )
    calibrated_model.fit(X_val, y_val)
    
    return calibrated_model


# ============================================
# BRIER SCORE FUNCTIONS
# ============================================

def brier_score_decomposition(y_true, y_pred_proba, n_bins=10):
    """
    Decompose Brier Score into Reliability, Resolution, and Uncertainty
    
    Returns:
        Dictionary with all components
    """
    brier = brier_score_loss(y_true, y_pred_proba)
    
    bins = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(y_pred_proba, bins) - 1
    
    base_rate = y_true.mean()
    
    reliability = 0
    resolution = 0
    
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.sum() > 0:
            bin_true_freq = y_true[mask].mean()
            bin_pred_freq = y_pred_proba[mask].mean()
            bin_weight = mask.sum() / len(y_true)
            
            reliability += bin_weight * (bin_pred_freq - bin_true_freq)**2
            resolution += bin_weight * (bin_true_freq - base_rate)**2
    
    uncertainty = base_rate * (1 - base_rate)
    
    return {
        'brier': brier,
        'reliability': reliability,
        'resolution': resolution,
        'uncertainty': uncertainty
    }


def brier_skill_score(y_true, y_pred_proba, baseline_prob=0.5):
    """
    Calculate Brier Skill Score (improvement over baseline)
    
    BSS > 0: Model better than baseline
    BSS = 0: Model equal to baseline
    BSS < 0: Model worse than baseline
    
    Benchmarks:
        > 0.20: Excellent
        0.10-0.20: Very good
        0.05-0.10: Good
        < 0.05: Marginal
    """
    bs_model = brier_score_loss(y_true, y_pred_proba)
    baseline_preds = np.full_like(y_pred_proba, baseline_prob)
    bs_baseline = brier_score_loss(y_true, baseline_preds)
    
    bss = 1 - (bs_model / bs_baseline)
    
    return bss


# ============================================
# BETTING FUNCTIONS
# ============================================

def american_odds_to_probability(odds):
    """Convert American odds to implied probability"""
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    else:
        return 100 / (odds + 100)


def decimal_odds_to_probability(decimal_odds):
    """Convert decimal odds to implied probability"""
    return 1 / decimal_odds


def calculate_ev(model_prob, odds, stake=100):
    """
    Calculate expected value of a bet
    
    Args:
        model_prob: Your model's probability of winning
        odds: American odds
        stake: Bet amount
    
    Returns:
        Expected value in dollars
    """
    if odds < 0:
        profit_multiplier = 100 / abs(odds)
    else:
        profit_multiplier = odds / 100
    
    profit_if_win = stake * profit_multiplier
    loss_if_lose = stake
    
    ev = (model_prob * profit_if_win) - ((1 - model_prob) * loss_if_lose)
    
    return ev


def kelly_criterion(model_prob, american_odds):
    """
    Calculate Kelly Criterion bet size
    
    Args:
        model_prob: Your model's win probability (0 to 1)
        american_odds: American odds format
    
    Returns:
        Kelly percentage (fraction of bankroll to bet)
    """
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


def fractional_kelly(model_prob, american_odds, fraction=0.25):
    """
    Calculate fractional Kelly bet size (RECOMMENDED)
    
    Common fractions:
    - 1/4 Kelly (0.25): Conservative, recommended for most
    - 1/2 Kelly (0.50): Moderate
    - Full Kelly (1.0): Aggressive, high variance
    """
    full_kelly = kelly_criterion(model_prob, american_odds)
    return full_kelly * fraction


def should_bet(model_prob, market_odds, min_edge=0.03, min_kelly=0.02):
    """
    Determine if a bet meets minimum thresholds
    
    Args:
        model_prob: Your model's probability
        market_odds: Market odds (American)
        min_edge: Minimum probability edge required (default 3%)
        min_kelly: Minimum Kelly percentage required (default 2%)
    
    Returns:
        (bool, str): Whether to bet and reason
    """
    market_prob = american_odds_to_probability(market_odds)
    edge = model_prob - market_prob
    kelly = kelly_criterion(model_prob, market_odds)
    
    if edge < min_edge:
        return False, f"Edge too small: {edge*100:.2f}% < {min_edge*100:.0f}%"
    
    if kelly < min_kelly:
        return False, f"Kelly too small: {kelly*100:.2f}% < {min_kelly*100:.0f}%"
    
    return True, f"✅ Bet: Edge {edge*100:.1f}%, Kelly {kelly*100:.1f}%"


def calculate_roi(bets_df):
    """
    Calculate ROI from historical betting data
    
    bets_df should have columns:
    - stake: Amount wagered
    - odds: American odds
    - result: 1 if won, 0 if lost
    
    Returns:
        Dictionary with ROI statistics
    """
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
    roi = (total_profit / total_staked) * 100 if total_staked > 0 else 0
    
    return {
        'total_staked': total_staked,
        'total_profit': total_profit,
        'roi': roi,
        'num_bets': len(bets_df),
        'win_rate': bets_df['result'].mean()
    }


# ============================================
# COMPREHENSIVE EVALUATION
# ============================================

def comprehensive_evaluation(y_true, y_pred_proba, y_pred_class=None, 
                            model_name="Model"):
    """
    Complete evaluation of probabilistic predictions
    
    Prints detailed metrics and returns summary dictionary
    """
    if y_pred_class is None:
        y_pred_class = (y_pred_proba > 0.5).astype(int)
    
    print(f"\n{'='*60}")
    print(f"  {model_name} - Complete Evaluation")
    print(f"{'='*60}\n")
    
    # Classification metrics
    print("CLASSIFICATION METRICS:")
    acc = accuracy_score(y_true, y_pred_class)
    print(f"  Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred_class).ravel()
    print(f"  True Positives: {tp}, True Negatives: {tn}")
    print(f"  False Positives: {fp}, False Negatives: {fn}")
    
    # Probabilistic metrics
    print("\nPROBABILISTIC METRICS:")
    ll = log_loss(y_true, y_pred_proba)
    print(f"  Log Loss: {ll:.4f}")
    
    brier = brier_score_loss(y_true, y_pred_proba)
    print(f"  Brier Score: {brier:.4f}")
    
    # Brier Skill Score
    baseline_brier = brier_score_loss(y_true, np.full_like(y_pred_proba, 0.5))
    bss = 1 - (brier / baseline_brier)
    print(f"  Brier Skill Score: {bss:.4f}")
    
    # ROC-AUC
    auc = roc_auc_score(y_true, y_pred_proba)
    print(f"  ROC-AUC: {auc:.4f}")
    
    # Calibration
    print("\nCALIBRATION:")
    ece = expected_calibration_error(y_true, y_pred_proba)
    print(f"  Expected Calibration Error: {ece:.4f}")
    
    if ece < 0.05:
        print("  → Excellent calibration")
    elif ece < 0.10:
        print("  → Good calibration")
    elif ece < 0.15:
        print("  → Moderate calibration")
    else:
        print("  → Poor calibration (needs fixing)")
    
    # Brier decomposition
    print("\nBRIER DECOMPOSITION:")
    decomp = brier_score_decomposition(y_true, y_pred_proba, n_bins=10)
    print(f"  Brier Score: {decomp['brier']:.4f}")
    print(f"  Reliability (↓ better): {decomp['reliability']:.4f}")
    print(f"  Resolution (↑ better): {decomp['resolution']:.4f}")
    print(f"  Uncertainty (fixed): {decomp['uncertainty']:.4f}")
    
    # Overall assessment
    print("\nOVERALL ASSESSMENT:")
    if acc > 0.68 and brier < 0.20 and ece < 0.10:
        print("  ✅ EXCELLENT - Ready for production")
    elif acc > 0.65 and brier < 0.23 and ece < 0.15:
        print("  ✅ GOOD - Suitable for launch")
    elif acc > 0.60 and brier < 0.25:
        print("  ⚠️  ADEQUATE - Needs improvement")
    else:
        print("  ❌ POOR - Significant work needed")
    
    print(f"\n{'='*60}\n")
    
    return {
        'accuracy': acc,
        'log_loss': ll,
        'brier_score': brier,
        'brier_skill_score': bss,
        'roc_auc': auc,
        'ece': ece,
        'decomposition': decomp
    }


def time_series_cross_validate(X, y, model_class, params, n_splits=5):
    """
    Perform time-series cross-validation
    
    Args:
        X: Features (should be chronologically ordered)
        y: Labels
        model_class: Model class (e.g., XGBClassifier)
        params: Model parameters dictionary
        n_splits: Number of CV folds
    
    Returns:
        Dictionary with CV results
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    
    cv_scores = {
        'accuracy': [],
        'log_loss': [],
        'brier_score': [],
        'ece': []
    }
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        # Train model
        model = model_class(**params)
        model.fit(X_train, y_train)
        
        # Predict probabilities
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Calculate metrics
        acc = accuracy_score(y_val, y_pred)
        ll = log_loss(y_val, y_pred_proba)
        bs = brier_score_loss(y_val, y_pred_proba)
        ece = expected_calibration_error(y_val, y_pred_proba)
        
        cv_scores['accuracy'].append(acc)
        cv_scores['log_loss'].append(ll)
        cv_scores['brier_score'].append(bs)
        cv_scores['ece'].append(ece)
        
        print(f"Fold {fold}: Acc={acc:.3f}, LogLoss={ll:.3f}, Brier={bs:.3f}, ECE={ece:.4f}")
    
    # Summary statistics
    print(f"\nCV Results (mean ± std):")
    print(f"Accuracy: {np.mean(cv_scores['accuracy']):.3f} ± {np.std(cv_scores['accuracy']):.3f}")
    print(f"Log Loss: {np.mean(cv_scores['log_loss']):.3f} ± {np.std(cv_scores['log_loss']):.3f}")
    print(f"Brier Score: {np.mean(cv_scores['brier_score']):.3f} ± {np.std(cv_scores['brier_score']):.3f}")
    print(f"ECE: {np.mean(cv_scores['ece']):.4f} ± {np.std(cv_scores['ece']):.4f}")
    
    return cv_scores


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    print("Model Evaluation Functions - Reference Implementation")
    print("Import these functions into your training scripts")
    print("\nExample usage:")
    print("""
    from model_evaluation_functions import (
        comprehensive_evaluation,
        plot_calibration_curve,
        apply_platt_scaling,
        kelly_criterion,
        calculate_roi
    )
    
    # Evaluate model
    results = comprehensive_evaluation(y_val, val_predictions, model_name="XGBoost v1.0")
    
    # Plot calibration
    plot_calibration_curve(y_val, val_predictions, model_name="XGBoost v1.0")
    
    # Calculate Kelly bet size
    kelly = kelly_criterion(model_prob=0.65, american_odds=-150)
    print(f"Kelly size: {kelly*100:.2f}%")
    """)