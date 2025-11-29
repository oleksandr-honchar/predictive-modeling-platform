
# EDA Quick Reference - Key Numbers

**Date:** November 26, 2025

## Critical Findings (Memorize These!)

### B2B Impact
- Home B2B penalty: **-8.3%** (56.7% → 48.4%)
- Away B2B penalty: **-5.4%** (45.6% → 40.2%)
- Total rest swing: **15.9%** (best to worst scenario)

### Rest Scenarios
| Scenario | Win Rate | Change from Baseline |
|----------|----------|---------------------|
| Both Rested | 55.8% | Baseline |
| Home Rested, Away B2B | 60.9% | +5.1% |
| Home B2B, Away Rested | 45.1% | -10.7% |
| Both B2B | 56.3% | +0.5% |

### Season Trends
- Home advantage drop: **6.6%** (58.6% early → 52.0% late)
- Early season volatility: **56% higher** (NET_RATING_DIFF std: 11.05 vs 7.09)
- WIN_PCT volatility: **79% higher** early season (0.375 vs 0.209)

### Top Features for Model
1. NET_RATING_PRIOR (home & away)
2. HOME_B2B & AWAY_B2B ⭐ (15.9% swing)
3. W_PCT_PRIOR (home & away)
4. Four Factors (EFG, TOV, OREB, FTA)
5. SEASON_PROGRESS (captures home advantage decline)

### Model Expectations
- Target accuracy: **68-70%** (good), **72-75%** (excellent)
- Early season: Expect -2 to -3% accuracy
- Late season: Expect +2 to +3% accuracy
- Target log loss: **< 0.60**

### Data Quality
- Total games: 5,085
- Smallest analysis bucket: 58 games (statistically valid)
- Most buckets: 200+ games (robust)
- Temporal integrity: ✅ All PRIOR features prevent data leakage

---
**Generated:** November 26, 2025 at 12:37 PM
