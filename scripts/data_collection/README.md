# NBA Data Collection Guide

## 🎯 Quick Start

### Prerequisites
```bash
# Activate your virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Install nba_api
pip install nba_api
```

### Step 1: Collect Game Data (~20-30 minutes)
```bash
cd /path/to/predictive-modeling-platform
python scripts/data_collection/collect_nba_games.py
```

**What this does:**
- Collects ALL 4 seasons (2021-22 through 2024-25)
- Expected: ~4,090 games total
- Output: `data/raw/nba/nba_games_all_data.csv`
- Includes automatic rate limiting (0.6s between requests)

### Step 2: Collect Advanced Statistics (~5-10 minutes)
```bash
python scripts/data_collection/collect_team_stats.py
```

**What this does:**
- Collects advanced team stats for all 4 seasons
- Includes: ORtg, DRtg, NetRtg, Pace, Four Factors
- Output: `data/raw/nba/nba_team_advanced_stats.csv`

---

## 📊 Expected Outputs

### File 1: `nba_games_all_data.csv`
**Size:** ~4,090 rows (one per team per game)
**Key Columns:**
- `GAME_ID` - Unique game identifier
- `GAME_DATE` - Date of game
- `MATCHUP` - Team matchup (e.g., "LAL vs. GSW")
- `WL` - Win/Loss result
- `PTS` - Points scored
- `FGM`, `FGA`, `FG_PCT` - Field goal stats
- `FG3M`, `FG3A`, `FG3_PCT` - Three-point stats
- `FTM`, `FTA`, `FT_PCT` - Free throw stats
- `OREB`, `DREB`, `REB` - Rebounding stats
- `AST`, `TOV`, `STL`, `BLK` - Other box score stats
- `PLUS_MINUS` - Point differential
- `SEASON` - Season identifier
- `TEAM_ABBR` - Team abbreviation

### File 2: `nba_team_advanced_stats.csv`
**Size:** ~120 rows (30 teams × 4 seasons)
**Key Columns:**
- `TEAM_ID`, `TEAM_NAME` - Team identifiers
- `SEASON` - Season identifier
- `W`, `L`, `W_PCT` - Win-loss record
- `OFF_RATING` - Offensive rating (points per 100 possessions)
- `DEF_RATING` - Defensive rating (points allowed per 100 possessions)
- `NET_RATING` - Net rating (OFF_RATING - DEF_RATING)
- `PACE` - Possessions per 48 minutes
- `EFG_PCT` - Effective field goal percentage
- `FTA_RATE` - Free throw attempt rate
- `TM_TOV_PCT` - Turnover percentage
- `OREB_PCT` - Offensive rebound percentage
- `OPP_EFG_PCT` - Opponent effective FG%
- `OPP_FTA_RATE` - Opponent FT rate
- `OPP_TOV_PCT` - Opponent turnover %
- `OPP_OREB_PCT` - Opponent offensive rebound %

---

## 🔍 Verification (After Collection)

Use this code to verify your data:

```python
import pandas as pd

# Load game data
games = pd.read_csv('data/raw/nba/nba_games_all_data.csv')
print(f"Total game records: {len(games):,}")
print(f"Unique games: {games['GAME_ID'].nunique():,}")
print(f"Seasons: {games['SEASON'].unique()}")
print(f"Date range: {games['GAME_DATE'].min()} to {games['GAME_DATE'].max()}")
print(f"Teams: {sorted(games['TEAM_ABBR'].unique())}")
print(f"\nMissing values:\n{games.isnull().sum()[games.isnull().sum() > 0]}")

# Load team stats
team_stats = pd.read_csv('data/raw/nba/nba_team_advanced_stats.csv')
print(f"\nTeam stats records: {len(team_stats):,}")
print(f"Seasons: {team_stats['SEASON'].unique()}")
print(f"\nSample advanced stats:")
print(team_stats[['TEAM_NAME', 'SEASON', 'OFF_RATING', 'DEF_RATING', 'NET_RATING']].head())
```

---

## 🐛 Troubleshooting

### Error: "Max retries exceeded"
**Solution:** NBA.com sometimes blocks requests. Wait 1-2 minutes and try again.

### Error: "Rate limit exceeded"
**Solution:** The scripts have built-in delays. If you still hit rate limits, increase `RATE_LIMIT_DELAY` in the scripts.

### Data is incomplete
**Solution:** Re-run the script. It will fetch missing data. The scripts are designed to be resumable.

### Import error: "No module named 'nba_api'"
**Solution:** Make sure you've activated your virtual environment and run `pip install nba_api`

---

## 📝 Helper Functions Reference

Both scripts include these helper functions:

```python
# Get team ID from abbreviation
from scripts.data_collection.collect_nba_games import get_all_team_ids

team_ids = get_all_team_ids()
lakers_id = team_ids['LAL']  # Returns: 1610612747
```

---

## ⏱️ Expected Execution Times

| Task | Expected Duration | API Calls |
|------|------------------|-----------|
| Game collection | 20-30 minutes | ~120 (30 teams × 4 seasons) |
| Team stats | 5-10 minutes | ~8 (2 endpoints × 4 seasons) |
| **Total** | **25-40 minutes** | **~128** |

---

## ✅ Next Steps

After data collection is complete:

1. ✅ Verify data using the verification code above
2. ✅ Open Jupyter notebook: `notebooks/01_eda.ipynb`
3. ✅ Perform exploratory data analysis
4. ✅ Document findings

---

## 📚 Additional Resources

- [nba_api Documentation](https://github.com/swar/nba_api)
- [Basketball-Reference Glossary](https://www.basketball-reference.com/about/glossary.html)
- [NBA Stats API Endpoints](https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints)

---

**Last Updated:** 2025-11-24
**Author:** Oleksandr