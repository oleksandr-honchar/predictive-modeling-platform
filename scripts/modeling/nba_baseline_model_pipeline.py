"""
NBA Prediction Baseline Model with Pipelines & Cross-Validation
================================================================

This script demonstrates:
1. Proper Pipeline construction for preprocessing + model
2. Time-series cross-validation for temporal data
3. GridSearchCV with pipelines for hyperparameter tuning
4. Preventing data leakage through pipeline encapsulation
5. Model comparison framework (Decision Tree → XGBoost)

Author: Oleksandr
Date: November 28, 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_validate, GridSearchCV
from sklearn.metrics import (
    accuracy_score, 
    brier_score_loss, 
    log_loss,
    make_scorer
)
from xgboost import XGBClassifier

# =============================================================================
# 1. CONFIGURATION
# =============================================================================

# File path
NBA_DATA_PATH = 'C:\\Users\\userPC\\projects\\predictive-modeling-platform\\data\\processed\\nba\\final\\nba_train_data_enhanced.csv'

# Feature sets for progressive model comparison
FEATURES_BASELINE = ['NET_RATING_DIFF']

FEATURES_FOUR_FACTORS = [
    'NET_RATING_DIFF',
    'EFG_PCT_DIFF',
    'TOV_PCT_DIFF',
    'OREB_PCT_DIFF',
    'FTA_RATE_DIFF'
]

FEATURES_FULL = FEATURES_FOUR_FACTORS + [
    'REST_ADVANTAGE',
    'HOME_B2B',
    'AWAY_B2B',
    'HOME_SEASON_PROGRESS',
    'AWAY_SEASON_PROGRESS'
]

# Target variable
TARGET = 'HOME_WIN'

# Cross-validation configuration
N_SPLITS = 5  # 5-fold time-series CV

# Random state for reproducibility
RANDOM_STATE = 42

# =============================================================================
# 2. DATA LOADING & PREPROCESSING
# =============================================================================

def load_data(file_path):
    """
    Load and prepare NBA data with temporal ordering preserved.
    
    Returns:
        df: DataFrame with games sorted chronologically
    """
    df = pd.read_csv(file_path)
    
    # Convert to datetime and sort chronologically (CRITICAL for time-series)
    if 'GAME_DATE' in df.columns:
        df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
        df = df.sort_values('GAME_DATE').reset_index(drop=True)
    
    # Drop rows with missing target
    df = df.dropna(subset=[TARGET])
    
    print(f"✓ Loaded {len(df):,} games")
    print(f"  Date range: {df['GAME_DATE'].min()} to {df['GAME_DATE'].max()}")
    print(f"  Home win rate: {df[TARGET].mean():.1%}")
    
    return df

# =============================================================================
# 3. PIPELINE CONSTRUCTION
# =============================================================================

def create_preprocessing_pipeline():
    """
    Create a preprocessing pipeline that:
    1. Imputes missing values (median strategy)
    2. Scales features (standardization)
    
    Why Pipeline?
    - Prevents data leakage: fit only on training data
    - Makes code cleaner and more maintainable
    - Easy to deploy: preprocessing travels with the model
    """
    return Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

def create_model_pipeline(model, preprocessing=True):
    """
    Create a complete pipeline with preprocessing + model.
    
    Args:
        model: Classifier instance (e.g., DecisionTreeClassifier())
        preprocessing: Whether to include preprocessing steps
        
    Returns:
        Pipeline object
    """
    if preprocessing:
        return Pipeline([
            ('preprocessor', create_preprocessing_pipeline()),
            ('classifier', model)
        ])
    else:
        # For tree-based models that don't need scaling
        return Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('classifier', model)
        ])

# =============================================================================
# 4. CROSS-VALIDATION FRAMEWORK
# =============================================================================

def evaluate_with_cv(pipeline, X, y, cv_splits=N_SPLITS, verbose=True):
    """
    Evaluate model using Time-Series Cross-Validation.
    
    Why TimeSeriesSplit?
    - Respects temporal order: never trains on future to predict past
    - Mimics real deployment: always predicting forward in time
    - Prevents data leakage in time-series data
    
    Args:
        pipeline: sklearn Pipeline object
        X: Feature DataFrame
        y: Target Series
        cv_splits: Number of CV folds
        verbose: Print detailed results
        
    Returns:
        dict: Cross-validation results
    """
    # Define custom scorers
    scoring = {
        'accuracy': 'accuracy',
        'log_loss': 'neg_log_loss',  # Note: negative because sklearn maximizes
        'brier_score': make_scorer(brier_score_loss, greater_is_better=False, needs_proba=True)
    }
    
    # Time-Series Cross-Validation
    tscv = TimeSeriesSplit(n_splits=cv_splits)
    
    # Perform cross-validation
    cv_results = cross_validate(
        pipeline, X, y,
        cv=tscv,
        scoring=scoring,
        return_train_score=True,
        n_jobs=-1  # Use all CPU cores
    )
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Time-Series Cross-Validation Results ({cv_splits} folds)")
        print(f"{'='*60}")
        print(f"Accuracy:     {-cv_results['test_accuracy'].mean():.4f} (±{cv_results['test_accuracy'].std():.4f})")
        print(f"Log Loss:     {-cv_results['test_log_loss'].mean():.4f} (±{cv_results['test_log_loss'].std():.4f})")
        print(f"Brier Score:  {-cv_results['test_brier_score'].mean():.4f} (±{cv_results['test_brier_score'].std():.4f})")
        print(f"{'='*60}\n")
    
    return cv_results

# =============================================================================
# 5. HYPERPARAMETER TUNING WITH GRIDSEARCH
# =============================================================================

def tune_hyperparameters(base_pipeline, param_grid, X, y, cv_splits=N_SPLITS):
    """
    Perform hyperparameter tuning using GridSearchCV with time-series CV.
    
    Why GridSearchCV with Pipeline?
    - Automatically handles train/val splits for each fold
    - Prevents data leakage: preprocessing fit only on training fold
    - Exhaustively searches parameter combinations
    
    Args:
        base_pipeline: Base pipeline to tune
        param_grid: Dictionary of parameters to search
        X: Feature DataFrame
        y: Target Series
        cv_splits: Number of CV folds
        
    Returns:
        GridSearchCV: Fitted GridSearchCV object with best parameters
    """
    # Time-Series Cross-Validation
    tscv = TimeSeriesSplit(n_splits=cv_splits)
    
    # Setup GridSearchCV
    grid_search = GridSearchCV(
        base_pipeline,
        param_grid,
        cv=tscv,
        scoring='neg_log_loss',  # Optimize for log loss
        n_jobs=-1,
        verbose=1,
        return_train_score=True
    )
    
    # Fit grid search
    print(f"\nSearching {len(param_grid)} parameters across {cv_splits} folds...")
    grid_search.fit(X, y)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Best Parameters: {grid_search.best_params_}")
    print(f"Best CV Score (neg_log_loss): {grid_search.best_score_:.4f}")
    print(f"{'='*60}\n")
    
    return grid_search

# =============================================================================
# 6. MODEL COMPARISON FRAMEWORK
# =============================================================================

def compare_models(X, y, feature_sets_dict):
    """
    Compare different models and feature sets using CV.
    
    Args:
        X: Full feature DataFrame
        y: Target Series
        feature_sets_dict: Dict mapping feature set name to feature list
        
    Returns:
        DataFrame: Comparison results
    """
    results = []
    
    for name, features in feature_sets_dict.items():
        print(f"\n{'*'*60}")
        print(f"Evaluating: {name}")
        print(f"Features: {len(features)}")
        print(f"{'*'*60}")
        
        X_subset = X[features]
        
        # Decision Tree
        dt_pipeline = create_model_pipeline(
            DecisionTreeClassifier(max_depth=5, random_state=RANDOM_STATE),
            preprocessing=False  # Decision trees don't need scaling
        )
        
        dt_cv = evaluate_with_cv(dt_pipeline, X_subset, y, verbose=False)
        results.append({
            'Feature Set': name,
            'Model': 'Decision Tree',
            'Accuracy': -dt_cv['test_accuracy'].mean(),
            'Log Loss': -dt_cv['test_log_loss'].mean(),
            'Brier Score': -dt_cv['test_brier_score'].mean()
        })
        
        # XGBoost
        xgb_pipeline = create_model_pipeline(
            XGBClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=RANDOM_STATE,
                eval_metric='logloss'
            ),
            preprocessing=False  # XGBoost doesn't need scaling
        )
        
        xgb_cv = evaluate_with_cv(xgb_pipeline, X_subset, y, verbose=False)
        results.append({
            'Feature Set': name,
            'Model': 'XGBoost',
            'Accuracy': -xgb_cv['test_accuracy'].mean(),
            'Log Loss': -xgb_cv['test_log_loss'].mean(),
            'Brier Score': -xgb_cv['test_brier_score'].mean()
        })
    
    results_df = pd.DataFrame(results)
    print(f"\n{'='*80}")
    print("MODEL COMPARISON SUMMARY")
    print(f"{'='*80}")
    print(results_df.to_string(index=False))
    print(f"{'='*80}\n")
    
    return results_df

# =============================================================================
# 7. BRIER SKILL SCORE CALCULATION
# =============================================================================

def calculate_brier_skill_score(y_true, y_pred_proba, baseline_prob):
    """
    Calculate Brier Skill Score to measure improvement over baseline.
    
    BSS = 1 - (BS_model / BS_baseline)
    
    Interpretation:
    - BSS > 0.15: Excellent improvement
    - BSS > 0.08: Good improvement
    - BSS > 0: Modest improvement
    - BSS < 0: Model worse than baseline
    
    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities
        baseline_prob: Baseline prediction (e.g., home win rate)
        
    Returns:
        float: Brier Skill Score
    """
    bs_model = brier_score_loss(y_true, y_pred_proba)
    baseline_preds = np.full_like(y_pred_proba, baseline_prob)
    bs_baseline = brier_score_loss(y_true, baseline_preds)
    bss = 1 - (bs_model / bs_baseline)
    
    print(f"Model Brier Score:    {bs_model:.4f}")
    print(f"Baseline Brier Score: {bs_baseline:.4f}")
    print(f"Brier Skill Score:    {bss:.4f}")
    
    if bss > 0.15:
        print("→ Excellent improvement over baseline! ✓✓✓")
    elif bss > 0.08:
        print("→ Good improvement over baseline ✓✓")
    elif bss > 0:
        print("→ Modest improvement over baseline ✓")
    else:
        print("→ WARNING: Model worse than baseline! ✗")
    
    return bss

# =============================================================================
# 8. FINAL TRAIN/VAL/TEST EVALUATION
# =============================================================================

def final_evaluation(pipeline, X_train, y_train, X_val, y_val, X_test, y_test):
    """
    Train final model and evaluate on validation and test sets.
    
    Args:
        pipeline: sklearn Pipeline
        X_train, y_train: Training data
        X_val, y_val: Validation data
        X_test, y_test: Test data (use ONCE only!)
        
    Returns:
        dict: Performance metrics
    """
    # Fit on training data
    pipeline.fit(X_train, y_train)
    
    # Validation set evaluation
    val_proba = pipeline.predict_proba(X_val)[:, 1]
    val_accuracy = accuracy_score(y_val, val_proba > 0.5)
    val_log_loss = log_loss(y_val, val_proba)
    val_brier = brier_score_loss(y_val, val_proba)
    
    print(f"\n{'='*60}")
    print("VALIDATION SET PERFORMANCE")
    print(f"{'='*60}")
    print(f"Accuracy:     {val_accuracy:.4f}")
    print(f"Log Loss:     {val_log_loss:.4f}")
    print(f"Brier Score:  {val_brier:.4f}")
    print(f"{'='*60}")
    
    # Test set evaluation (ONLY ONCE!)
    test_proba = pipeline.predict_proba(X_test)[:, 1]
    test_accuracy = accuracy_score(y_test, test_proba > 0.5)
    test_log_loss = log_loss(y_test, test_proba)
    test_brier = brier_score_loss(y_test, test_proba)
    
    print(f"\n{'='*60}")
    print("TEST SET PERFORMANCE (FINAL EVALUATION)")
    print(f"{'='*60}")
    print(f"Accuracy:     {test_accuracy:.4f}")
    print(f"Log Loss:     {test_log_loss:.4f}")
    print(f"Brier Score:  {test_brier:.4f}")
    print(f"{'='*60}\n")
    
    # Calculate Brier Skill Score
    baseline_prob = y_train.mean()
    print(f"\nBaseline (home win rate): {baseline_prob:.4f}")
    bss = calculate_brier_skill_score(y_test, test_proba, baseline_prob)
    
    return {
        'val_accuracy': val_accuracy,
        'val_log_loss': val_log_loss,
        'val_brier': val_brier,
        'test_accuracy': test_accuracy,
        'test_log_loss': test_log_loss,
        'test_brier': test_brier,
        'brier_skill_score': bss
    }

# =============================================================================
# 9. MAIN EXECUTION
# =============================================================================

def main():
    """
    Main execution flow demonstrating all concepts.
    """
    print("\n" + "="*80)
    print("NBA PREDICTION MODEL - PIPELINE & CROSS-VALIDATION DEMO")
    print("="*80 + "\n")
    
    # Load data
    df = load_data(NBA_DATA_PATH)
    
    # Prepare features and target
    X = df[FEATURES_FULL]
    y = df[TARGET]
    
    # =========================================================================
    # PART 1: MODEL COMPARISON WITH CROSS-VALIDATION
    # =========================================================================
    print("\n" + "="*80)
    print("PART 1: MODEL COMPARISON")
    print("="*80)
    
    feature_sets = {
        'Baseline (Net Rating)': FEATURES_BASELINE,
        'Four Factors': FEATURES_FOUR_FACTORS,
        'Full Model': FEATURES_FULL
    }
    
    comparison_results = compare_models(X, y, feature_sets)
    
    # =========================================================================
    # PART 2: HYPERPARAMETER TUNING EXAMPLE
    # =========================================================================
    print("\n" + "="*80)
    print("PART 2: HYPERPARAMETER TUNING (XGBoost)")
    print("="*80)
    
    # Create base pipeline
    xgb_pipeline = create_model_pipeline(
        XGBClassifier(random_state=RANDOM_STATE, eval_metric='logloss'),
        preprocessing=False
    )
    
    # Define parameter grid
    param_grid = {
        'classifier__max_depth': [3, 4, 5],
        'classifier__learning_rate': [0.05, 0.1],
        'classifier__n_estimators': [100, 200]
    }
    
    # Tune hyperparameters
    X_full = df[FEATURES_FULL]
    grid_search = tune_hyperparameters(xgb_pipeline, param_grid, X_full, y)
    
    # =========================================================================
    # PART 3: FINAL TRAIN/VAL/TEST SPLIT EVALUATION
    # =========================================================================
    print("\n" + "="*80)
    print("PART 3: FINAL EVALUATION ON HOLD-OUT SETS")
    print("="*80)
    
    # Create temporal splits (70/15/15)
    split_idx_val = int(0.70 * len(df))
    split_idx_test = int(0.85 * len(df))
    
    train_df = df.iloc[:split_idx_val]
    val_df = df.iloc[split_idx_val:split_idx_test]
    test_df = df.iloc[split_idx_test:]
    
    X_train = train_df[FEATURES_FULL]
    y_train = train_df[TARGET]
    X_val = val_df[FEATURES_FULL]
    y_val = val_df[TARGET]
    X_test = test_df[FEATURES_FULL]
    y_test = test_df[TARGET]
    
    print(f"\nTrain set: {len(train_df):,} games")
    print(f"Val set:   {len(val_df):,} games")
    print(f"Test set:  {len(test_df):,} games")
    
    # Use best model from grid search
    best_pipeline = grid_search.best_estimator_
    
    # Final evaluation
    final_metrics = final_evaluation(
        best_pipeline,
        X_train, y_train,
        X_val, y_val,
        X_test, y_test
    )
    
    print("\n" + "="*80)
    print("PIPELINE & CROSS-VALIDATION DEMO COMPLETE!")
    print("="*80 + "\n")
    
    return comparison_results, grid_search, final_metrics

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    comparison_results, grid_search, final_metrics = main()