# Understanding Pipelines & Cross-Validation in NBA Predictions

## Table of Contents
1. [Why Pipelines Matter](#why-pipelines-matter)
2. [Pipeline Construction](#pipeline-construction)
3. [Preventing Data Leakage](#preventing-data-leakage)
4. [Time-Series Cross-Validation](#time-series-cross-validation)
5. [GridSearchCV with Pipelines](#gridsearchcv-with-pipelines)
6. [Practical Examples](#practical-examples)

---

## Why Pipelines Matter

### The Problem Without Pipelines

**❌ WRONG WAY (Data Leakage):**
```python
# Fit scaler on ALL data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Uses test data info!

# Split AFTER scaling
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)

# Model sees test data statistics during training
model.fit(X_train, y_train)
```

**Why this is wrong:**
- Scaler learns mean/std from entire dataset (including test set)
- Model indirectly sees test set information
- Results in **overly optimistic performance estimates**
- Will fail in production (new data has different statistics)

### The Solution: Pipelines

**✅ RIGHT WAY (No Data Leakage):**
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),      # Step 1: Scale
    ('classifier', RandomForestClassifier())  # Step 2: Classify
])

# Split BEFORE any processing
X_train, X_test, y_train, y_test = train_test_split(X, y)

# Fit pipeline (scaler learns ONLY from training data)
pipeline.fit(X_train, y_train)

# Predict (scaler transforms using training statistics)
predictions = pipeline.predict(X_test)
```

**Why this is correct:**
- Scaler fits on training data only
- Test data never influences preprocessing
- Results are **honest estimates** of production performance
- Preprocessing travels with model (easy deployment)

---

## Pipeline Construction

### Basic Structure

A Pipeline is a sequence of transformers ending with a classifier/regressor.

```python
pipeline = Pipeline([
    ('step1_name', Transformer1()),   # Must have fit() and transform()
    ('step2_name', Transformer2()),   # Must have fit() and transform()
    ('final_step_name', Estimator())  # Must have fit() and predict()
])
```

### Common Pipeline Components

#### 1. Imputation (Handling Missing Values)

```python
from sklearn.impute import SimpleImputer

# Strategy options: 'mean', 'median', 'most_frequent', 'constant'
imputer = SimpleImputer(strategy='median')

# For NBA data: median is robust to outliers
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('classifier', model)
])
```

**When to use:**
- Your data has missing values (NaN)
- Want to avoid dropping rows/columns
- Tree-based models can handle NaN, but safer to impute

**Why median for NBA:**
- Robust to extreme outliers (e.g., 70-point games)
- Better than mean for skewed distributions
- Conservative approach for betting models

#### 2. Scaling (Standardization)

```python
from sklearn.preprocessing import StandardScaler

# Transforms features to mean=0, std=1
scaler = StandardScaler()

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', model)
])
```

**When to use:**
- Logistic Regression (requires scaled features)
- Neural Networks (requires scaled features)
- K-Nearest Neighbors (distance-based)
- SVM (distance-based)

**When NOT to use:**
- Decision Trees (scale-invariant)
- Random Forests (scale-invariant)
- XGBoost (scale-invariant)
- Naive Bayes (probability-based)

**For NBA predictions:**
```python
# Tree-based models (NO scaling needed)
xgb_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('classifier', XGBClassifier())
])

# Logistic Regression (SCALING needed)
lr_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression())
])
```

#### 3. Feature Selection

```python
from sklearn.feature_selection import SelectKBest, f_classif

pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('feature_selection', SelectKBest(f_classif, k=10)),
    ('classifier', model)
])
```

**Use cases:**
- Too many features (>50)
- Want to reduce overfitting
- Need to identify most important features

### Complete Preprocessing Pipeline

```python
def create_preprocessing_pipeline():
    """
    Complete preprocessing that handles common issues.
    """
    return Pipeline([
        ('imputer', SimpleImputer(strategy='median')),  # Handle NaN
        ('scaler', StandardScaler())                     # Standardize
    ])

# Usage
preprocessing = create_preprocessing_pipeline()

# Can be used standalone
X_train_processed = preprocessing.fit_transform(X_train)
X_test_processed = preprocessing.transform(X_test)

# Or integrated into model pipeline
full_pipeline = Pipeline([
    ('preprocessor', preprocessing),
    ('classifier', model)
])
```

---

## Preventing Data Leakage

### What is Data Leakage?

**Definition:** Using information in your training data that won't be available when making real predictions.

### Types of Data Leakage

#### 1. **Preprocessing Leakage** (Most Common)

**❌ WRONG:**
```python
# Fit on all data
scaler.fit(X)  # Includes test set!
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**✅ RIGHT:**
```python
# Fit only on training data
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**Pipeline automatically does this:**
```python
pipeline.fit(X_train, y_train)  # Fits scaler on X_train only
pipeline.predict(X_test)         # Uses X_train statistics
```

#### 2. **Temporal Leakage** (Critical for NBA)

**❌ WRONG:**
```python
# Random split - trains on future to predict past!
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
```

**✅ RIGHT:**
```python
# Chronological split - respects time order
split_idx = int(0.8 * len(df))
train_df = df.iloc[:split_idx]   # Games 1-4000
test_df = df.iloc[split_idx:]    # Games 4001-5000
```

#### 3. **Feature Leakage** (Using Future Information)

**❌ WRONG:**
```python
# Using season averages (includes future games!)
df['season_ppg'] = df.groupby(['SEASON', 'TEAM'])['PTS'].transform('mean')
```

**✅ RIGHT:**
```python
# Using expanding window (only past games)
df['season_ppg'] = df.groupby(['SEASON', 'TEAM'])['PTS'].expanding().mean().shift(1)
```

**For NBA predictions:**
```python
# ❌ DON'T USE: HOME_NET_RATING (includes this game's result!)
# ✅ USE: HOME_NET_RATING_PRIOR (only games before this one)

features = [
    'HOME_NET_RATING_PRIOR',  # ✅ Safe
    'AWAY_NET_RATING_PRIOR',  # ✅ Safe
    'NET_RATING_DIFF',        # ✅ Safe (computed from _PRIOR)
]
```

#### 4. **Target Leakage** (Using Outcome in Features)

**❌ WRONG:**
```python
# HOME_PTS is the game result! Can't use to predict winner
features = ['HOME_PTS', 'AWAY_PTS', 'HOME_NET_RATING']
```

**✅ RIGHT:**
```python
# Only use information available BEFORE game
features = ['HOME_NET_RATING_PRIOR', 'AWAY_NET_RATING_PRIOR']
```

### Leakage Detection Checklist

```python
# 1. Check for suspiciously high accuracy
if test_accuracy > 0.80:
    print("⚠️ WARNING: Accuracy too high, check for leakage!")

# 2. Verify temporal ordering
assert df['GAME_DATE'].is_monotonic_increasing

# 3. Confirm train/test temporal separation
assert train_df['GAME_DATE'].max() < test_df['GAME_DATE'].min()

# 4. Check feature names for leakage indicators
leakage_indicators = ['_SEASON', '_TOTAL', 'RESULT', 'OUTCOME']
for col in features:
    if any(indicator in col for indicator in leakage_indicators):
        print(f"⚠️ WARNING: {col} might contain leakage")

# 5. Verify all features end with _PRIOR or are differentials
for col in features:
    if not (col.endswith('_PRIOR') or 'DIFF' in col or 'B2B' in col):
        print(f"⚠️ WARNING: {col} might not be point-in-time")
```

---

## Time-Series Cross-Validation

### Why Standard K-Fold Fails for Time-Series

**❌ Standard K-Fold (Random Folds):**
```python
from sklearn.model_selection import KFold

kfold = KFold(n_splits=5, shuffle=True)  # ❌ Shuffles data!

# Result: Trains on 2024 games to predict 2022 games
# This is TEMPORAL LEAKAGE!
```

**Problem:**
- Randomly assigns games to folds
- Training set contains future games
- Validation set contains past games
- **Model sees the future!**

### TimeSeriesSplit: The Correct Approach

**✅ Time-Series Split:**
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)

# Expanding window approach:
# Fold 1: Train [1:1000] → Val [1001:2000]
# Fold 2: Train [1:2000] → Val [2001:3000]
# Fold 3: Train [1:3000] → Val [3001:4000]
# Fold 4: Train [1:4000] → Val [4001:5000]
# Fold 5: Train [1:5000] → Val [5001:6000]
```

**Why this works:**
- Always trains on past, validates on future
- Mimics real deployment scenario
- No temporal leakage
- Progressive model validation

### Implementing Time-Series CV

```python
from sklearn.model_selection import TimeSeriesSplit, cross_validate

# Create time-series splitter
tscv = TimeSeriesSplit(n_splits=5)

# Perform cross-validation
cv_results = cross_validate(
    pipeline,
    X, y,
    cv=tscv,                    # Time-series splits
    scoring='neg_log_loss',     # Metric to optimize
    return_train_score=True,    # Track training performance
    n_jobs=-1                   # Use all CPU cores
)

# Results
print(f"Mean CV Score: {-cv_results['test_score'].mean():.4f}")
print(f"Std CV Score: {cv_results['test_score'].std():.4f}")
```

### Multiple Metrics

```python
from sklearn.metrics import make_scorer, brier_score_loss

# Define multiple scoring metrics
scoring = {
    'accuracy': 'accuracy',
    'log_loss': 'neg_log_loss',
    'brier': make_scorer(brier_score_loss, greater_is_better=False, needs_proba=True)
}

# Cross-validate with multiple metrics
cv_results = cross_validate(
    pipeline, X, y,
    cv=tscv,
    scoring=scoring,
    return_train_score=True
)

# Access results
print(f"Accuracy: {cv_results['test_accuracy'].mean():.4f}")
print(f"Log Loss: {-cv_results['test_log_loss'].mean():.4f}")
print(f"Brier:    {-cv_results['test_brier'].mean():.4f}")
```

### Visualizing CV Splits

```python
import matplotlib.pyplot as plt

def plot_cv_splits(cv, X, y):
    """Visualize how TimeSeriesSplit creates folds."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for i, (train_idx, val_idx) in enumerate(cv.split(X)):
        # Plot training indices
        ax.scatter(train_idx, [i] * len(train_idx), 
                   c='blue', marker='_', s=100, label='Train' if i == 0 else '')
        
        # Plot validation indices
        ax.scatter(val_idx, [i] * len(val_idx), 
                   c='red', marker='_', s=100, label='Validation' if i == 0 else '')
    
    ax.set_xlabel('Game Index')
    ax.set_ylabel('CV Fold')
    ax.set_title('Time-Series Cross-Validation Splits')
    ax.legend()
    plt.tight_layout()
    plt.show()

# Usage
tscv = TimeSeriesSplit(n_splits=5)
plot_cv_splits(tscv, X, y)
```

---

## GridSearchCV with Pipelines

### Basic GridSearchCV

```python
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

# Define parameter grid
param_grid = {
    'max_depth': [3, 4, 5, 6],
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [100, 200, 300]
}

# Create model
model = XGBClassifier(random_state=42)

# Setup GridSearchCV
grid_search = GridSearchCV(
    model,
    param_grid,
    cv=TimeSeriesSplit(n_splits=5),  # Time-series CV
    scoring='neg_log_loss',
    n_jobs=-1,
    verbose=2
)

# Fit
grid_search.fit(X_train, y_train)

# Results
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best CV Score: {grid_search.best_score_:.4f}")
```

### GridSearchCV with Pipelines

**Key Difference:** Need to prefix parameter names with step name

```python
from sklearn.pipeline import Pipeline

# Create pipeline
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('classifier', XGBClassifier(random_state=42))
])

# Parameter grid with pipeline naming
param_grid = {
    'classifier__max_depth': [3, 4, 5, 6],           # Note: classifier__
    'classifier__learning_rate': [0.01, 0.05, 0.1],  # Note: classifier__
    'classifier__n_estimators': [100, 200, 300]      # Note: classifier__
}

# GridSearchCV
grid_search = GridSearchCV(
    pipeline,  # Use pipeline instead of model
    param_grid,
    cv=TimeSeriesSplit(n_splits=5),
    scoring='neg_log_loss',
    n_jobs=-1,
    verbose=2
)

# Fit
grid_search.fit(X_train, y_train)
```

**Naming Convention:**
- `step_name__parameter_name`
- Double underscore `__` separates step from parameter
- Example: `classifier__max_depth` → max_depth of classifier step

### Tuning Multiple Steps

```python
pipeline = Pipeline([
    ('imputer', SimpleImputer()),
    ('scaler', StandardScaler()),
    ('classifier', XGBClassifier())
])

# Tune imputation strategy AND model hyperparameters
param_grid = {
    'imputer__strategy': ['mean', 'median'],               # Imputation step
    'classifier__max_depth': [3, 4, 5],                    # Classifier step
    'classifier__learning_rate': [0.05, 0.1]               # Classifier step
}

grid_search = GridSearchCV(pipeline, param_grid, cv=tscv)
grid_search.fit(X_train, y_train)
```

### Accessing Results

```python
# Best parameters
print(grid_search.best_params_)
# {'classifier__max_depth': 4, 'classifier__learning_rate': 0.05, ...}

# Best score
print(f"Best CV Score: {grid_search.best_score_:.4f}")

# Best estimator (fitted pipeline)
best_pipeline = grid_search.best_estimator_

# Use best pipeline for predictions
predictions = best_pipeline.predict(X_test)
probabilities = best_pipeline.predict_proba(X_test)

# Detailed results
results_df = pd.DataFrame(grid_search.cv_results_)
results_df[['params', 'mean_test_score', 'std_test_score']].sort_values(
    'mean_test_score', ascending=False
).head()
```

### Efficient Search Strategies

#### 1. RandomizedSearchCV (Faster)

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

# Define distributions instead of discrete values
param_distributions = {
    'classifier__max_depth': randint(3, 10),           # Random integers 3-9
    'classifier__learning_rate': uniform(0.01, 0.2),   # Random floats 0.01-0.21
    'classifier__n_estimators': randint(50, 500)       # Random integers 50-499
}

# RandomizedSearchCV
random_search = RandomizedSearchCV(
    pipeline,
    param_distributions,
    n_iter=50,  # Try 50 random combinations
    cv=TimeSeriesSplit(n_splits=5),
    scoring='neg_log_loss',
    n_jobs=-1,
    random_state=42
)

random_search.fit(X_train, y_train)
```

**When to use:**
- Large parameter spaces (>100 combinations)
- Continuous parameters (learning_rate, regularization)
- Want faster initial exploration

#### 2. Halving GridSearch (sklearn 1.0+)

```python
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV

# Progressive elimination of bad parameters
halving_search = HalvingGridSearchCV(
    pipeline,
    param_grid,
    cv=TimeSeriesSplit(n_splits=3),  # Fewer splits initially
    factor=3,  # Eliminate 2/3 of candidates each iteration
    resource='n_samples',  # Use more data progressively
    scoring='neg_log_loss',
    n_jobs=-1
)

halving_search.fit(X_train, y_train)
```

**Benefits:**
- Much faster than GridSearchCV
- Automatically eliminates poor parameters early
- Focuses computational resources on promising candidates

---

## Practical Examples

### Example 1: Complete NBA Baseline Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_validate

# Define features
features = [
    'NET_RATING_DIFF',
    'HOME_NET_RATING_PRIOR',
    'AWAY_NET_RATING_PRIOR',
    'REST_ADVANTAGE',
    'HOME_B2B',
    'AWAY_B2B'
]

# Create pipeline
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('classifier', XGBClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        random_state=42,
        eval_metric='logloss'
    ))
])

# Time-series cross-validation
tscv = TimeSeriesSplit(n_splits=5)

# Evaluate
cv_results = cross_validate(
    pipeline,
    X[features], y,
    cv=tscv,
    scoring={
        'accuracy': 'accuracy',
        'log_loss': 'neg_log_loss'
    },
    return_train_score=True,
    n_jobs=-1
)

print(f"CV Accuracy: {cv_results['test_accuracy'].mean():.4f} "
      f"(±{cv_results['test_accuracy'].std():.4f})")
print(f"CV Log Loss: {-cv_results['test_log_loss'].mean():.4f} "
      f"(±{cv_results['test_log_loss'].std():.4f})")
```

### Example 2: Progressive Feature Engineering

```python
# Define feature sets
feature_sets = {
    'Baseline': ['NET_RATING_DIFF'],
    'Four Factors': [
        'NET_RATING_DIFF',
        'EFG_PCT_DIFF',
        'TOV_PCT_DIFF',
        'OREB_PCT_DIFF',
        'FTA_RATE_DIFF'
    ],
    'Full Model': [
        'NET_RATING_DIFF',
        'EFG_PCT_DIFF',
        'TOV_PCT_DIFF',
        'OREB_PCT_DIFF',
        'FTA_RATE_DIFF',
        'REST_ADVANTAGE',
        'HOME_B2B',
        'AWAY_B2B'
    ]
}

# Compare feature sets
results = []
for name, features in feature_sets.items():
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('classifier', XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            random_state=42
        ))
    ])
    
    cv_results = cross_validate(
        pipeline,
        X[features], y,
        cv=TimeSeriesSplit(n_splits=5),
        scoring='neg_log_loss',
        n_jobs=-1
    )
    
    results.append({
        'Feature Set': name,
        'Features': len(features),
        'Log Loss': -cv_results['test_score'].mean(),
        'Std': cv_results['test_score'].std()
    })

results_df = pd.DataFrame(results)
print(results_df)
```

### Example 3: Complete Hyperparameter Tuning

```python
# Create base pipeline
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('classifier', XGBClassifier(random_state=42, eval_metric='logloss'))
])

# Extensive parameter grid
param_grid = {
    'classifier__max_depth': [3, 4, 5, 6],
    'classifier__learning_rate': [0.01, 0.05, 0.1],
    'classifier__n_estimators': [100, 200, 300],
    'classifier__subsample': [0.8, 0.9, 1.0],
    'classifier__colsample_bytree': [0.8, 0.9, 1.0]
}

# GridSearchCV with time-series CV
grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=TimeSeriesSplit(n_splits=5),
    scoring='neg_log_loss',
    n_jobs=-1,
    verbose=2
)

# Fit
grid_search.fit(X_train, y_train)

# Best model
best_pipeline = grid_search.best_estimator_

# Evaluate on test set (ONCE!)
test_proba = best_pipeline.predict_proba(X_test)[:, 1]
test_log_loss = log_loss(y_test, test_proba)

print(f"\nBest Parameters: {grid_search.best_params_}")
print(f"CV Log Loss: {-grid_search.best_score_:.4f}")
print(f"Test Log Loss: {test_log_loss:.4f}")
```

---

## Summary: Key Takeaways

### ✅ Always Use Pipelines When:
1. You have preprocessing steps (imputation, scaling)
2. You need to prevent data leakage
3. You want reproducible, deployable models
4. You're doing hyperparameter tuning

### ✅ Always Use TimeSeriesSplit When:
1. Working with time-ordered data (NBA games)
2. Need to respect temporal causality
3. Want realistic performance estimates
4. Simulating real deployment scenario

### ✅ Key Concepts Mastered:
1. **Pipeline construction**: Automatic preprocessing
2. **Data leakage prevention**: Fit on train only
3. **Time-series CV**: Respect temporal order
4. **GridSearchCV**: Efficient hyperparameter tuning
5. **Pipeline naming**: `step__parameter` convention

### 🎯 Next Steps:
1. Run the baseline model code
2. Experiment with different feature sets
3. Try different preprocessing steps
4. Compare models systematically
5. Move to advanced feature engineering

---

## Common Debugging Tips

### Pipeline Not Working?

```python
# Check pipeline steps
print(pipeline.named_steps)

# Access specific step
scaler = pipeline.named_steps['scaler']
print(f"Mean: {scaler.mean_}")

# Get feature names after preprocessing
if hasattr(pipeline, 'get_feature_names_out'):
    print(pipeline.get_feature_names_out())
```

### Cross-Validation Taking Too Long?

```python
# Reduce CV folds
tscv = TimeSeriesSplit(n_splits=3)  # Instead of 5

# Use subset of data for initial testing
X_subset = X.iloc[:1000]
y_subset = y.iloc[:1000]

# Reduce parameter grid
param_grid = {
    'classifier__max_depth': [4],  # Single value for testing
    'classifier__learning_rate': [0.05]
}
```

### Unexpected Results?

```python
# Verify temporal ordering
assert df['GAME_DATE'].is_monotonic_increasing

# Check for data leakage
if accuracy > 0.80:
    print("⚠️ Suspiciously high - check for leakage!")

# Inspect feature distributions
print(X_train.describe())
print(X_test.describe())  # Should be similar!
```

---

**You're now ready to build production-grade NBA prediction models!** 🏀📊