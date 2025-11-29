# Friday, November 28, 2025 - Work Preparation

## Overview
**Day:** 12 of 42  
**Week:** Week 2  
**Focus:** Feature Planning & Engineering Design  
**Total Hours:** 8 hours

---

## Schedule Breakdown

### Morning Block (8:00 AM - 12:00 PM) - 4 hours

#### Session 1: Intermediate ML (8:00-10:00 AM)
**Topics:**
- [x] Pipelines
- [x] Cross-Validation (practical applications)

**Objectives:**
- Understand sklearn Pipeline construction
- Learn to prevent data leakage in preprocessing
- Apply cross-validation to real models
- Understand GridSearchCV with pipelines

**Pre-reading:**
- Review yesterday's cross-validation notes
- Sklearn Pipeline documentation if needed

---

#### Session 2: Feature Planning (10:30 AM-12:00 PM)
**Topics:**
- [x] List all available NBA features
- [x] Prioritize by importance

**Objectives:**
1. **Inventory Features**
   - Review `NBA_API_Data_Fields_Complete.md`
   - Review `Data_Fields_Quick_Reference.md`
   - List all `_PRIOR` columns in `nba_training_data.csv`

2. **Categorize Features**
   - Dean Oliver's Four Factors features
   - Advanced metrics (Net Rating, PIE, etc.)
   - Rest/schedule features
   - Derived features to create

3. **Prioritize by Importance**
   - Tier 1: Core Four Factors + Net Rating
   - Tier 2: Advanced metrics
   - Tier 3: Rest/schedule features
   - Tier 4: Experimental features

**Deliverables:**
- Feature inventory spreadsheet/document
- Priority ranking with rationale
- Gap analysis (what data do we need but don't have?)

---

### Afternoon Block (2:00 PM - 6:00 PM) - 4 hours

#### Session 3: Feature Engineering Design (2:00-4:00 PM)
**Topics:**
- [ ] Rolling averages (L5, L10)
- [ ] Rest days & back-to-backs
- [ ] Head-to-head records

**Objectives:**

**1. Rolling Averages Design**
- Define window sizes (L3, L5, L10, L15?)
- Which stats to roll (NET_RATING, EFG_PCT, etc.)
- How to handle early season (< 5 games played)
- Exponential vs simple moving average?

**2. Rest Features Enhancement**
- Already have: HOME_DAYS_REST, AWAY_DAYS_REST, REST_ADVANTAGE
- Add: Days since last game by opponent
- Add: Travel distance (if implementing)
- Add: Timezone changes (if implementing)

**3. Head-to-Head Records**
- Season H2H records
- Recent H2H (last 5 meetings)
- Home vs away H2H splits
- Playoff history (if relevant)

**Deliverables:**
- Feature engineering specification document
- Pseudocode for key feature calculations
- Data requirements list

---

#### Session 4: Week 2 Documentation (4:30-6:00 PM)
**Topics:**
- [ ] Document data collected
- [ ] Summarize EDA findings

**Objectives:**

**1. Data Collection Summary**
- Total games collected (3,924)
- Date range (Oct 2022 - Nov 2025)
- Data quality issues found and resolved
- API reliability notes
- Checkpoint/retry system performance

**2. EDA Findings Summary**
- Key correlations discovered
- Net Rating Differential insights
- Four Factors analysis
- Home court advantage quantification
- Season progression patterns
- Data quality validations

**3. Week 2 Accomplishments Document**
- Daily progress log
- Hours invested
- Documentation created
- Knowledge gained
- Ahead/behind schedule assessment

**Deliverables:**
- Week 2 summary document
- Data collection documentation
- EDA findings report

---

## Files to Have Open

### Reference Documents
1. `NBA_API_Data_Fields_Complete.md` - All available fields
2. `Data_Fields_Quick_Reference.md` - Quick reference
3. `Model_Evaluation_Complete_Guide.md` - Yesterday's work
4. `How_NBA_Analytics_Work.md` - Four Factors framework
5. `four_factors_deep_dive.md` - Detailed analysis

### Data Files
1. `nba_training_data.csv` - Main dataset (3,924 games)
2. `nba_train_data.csv` - Original dataset (5,085 games)

### Code Files
1. `model_evaluation_functions.py` - Evaluation utilities
2. Any EDA notebooks created earlier

---

## Pre-Session Setup Checklist

### Before Starting Work
- [ ] Review yesterday's accomplishments
- [ ] Read through this preparation document
- [ ] Have all reference files accessible
- [ ] Open Jupyter notebook or Python environment
- [ ] Coffee/tea ready ☕
- [ ] Phone on silent 📵

### Environment Check
- [ ] Python environment active
- [ ] All libraries imported (pandas, numpy, sklearn, xgboost)
- [ ] Data loaded and verified
- [ ] Working directory organized

---

## Key Questions to Answer Tomorrow

### Feature Planning Questions
1. Which features from `_PRIOR` columns should be baseline?
2. Which derived features will provide most value?
3. What's the minimum feature set for V1.0?
4. What features are stretch goals for V2.0?

### Feature Engineering Questions
1. What window size for rolling averages?
2. How to handle early season sparse data?
3. Should we weight recent games more heavily?
4. How to encode categorical features (if any)?

### Documentation Questions
1. What were the biggest challenges in Week 2?
2. What decisions need to be documented?
3. What code needs to be cleaned and archived?
4. What learnings should be shared in methodology?

---

## Expected Outputs by End of Day

### Morning Outputs
1. ✅ Completed Intermediate ML lessons
2. ✅ Feature inventory document (all 183 columns categorized)
3. ✅ Feature priority ranking with Tier 1/2/3/4 classification
4. ✅ Gap analysis of missing data

### Afternoon Outputs
1. ✅ Feature engineering specification
2. ✅ Pseudocode for rolling average calculations
3. ✅ Week 2 documentation complete
4. ✅ Data collection summary
5. ✅ EDA findings report

---

## Success Criteria

### Morning Session Success
- Clear understanding of which features to use
- Prioritized list ready for implementation
- No ambiguity about what to build

### Afternoon Session Success
- Detailed plan for feature engineering
- Week 2 work fully documented
- Ready to start coding on Monday

### Overall Day Success
- 8 hours of focused work completed
- All scheduled tasks finished
- Documentation current and organized
- Confident about next week's execution

---

## Tomorrow Evening: Self-Assessment

At end of day, rate yourself on:
1. **Focus & Productivity** (1-10): ___
2. **Task Completion** (1-10): ___
3. **Quality of Output** (1-10): ___
4. **Energy Level** (1-10): ___

**What went well:**
- 

**What could improve:**
- 

**Key decisions made:**
- 

**Blockers encountered:**
- 

---

## Weekend Planning Preview

After tomorrow's work, you'll have:
- Complete feature plan ready
- All Week 2 work documented
- Clear roadmap for Week 3 implementation

**Weekend activities (if working):**
- Light code exploration
- Review feature engineering pseudocode
- Optional: Start building feature pipeline

**Or take the weekend off - you're ahead of schedule! 🎉**

---

## Motivation Boost 🚀

### Progress Reminder
- Day 12 of 42 (28% through pre-launch)
- 3-4 days ahead of schedule
- 37,000+ words of documentation created
- Dataset complete and validated
- Deep understanding of evaluation methods

### What You've Accomplished
Week 1: Full project infrastructure, data collection strategy  
Week 2: Data collection complete, EDA done, evaluation mastery

**You're crushing it!** Tomorrow is about translating knowledge into actionable plans.

### Week 3 Preview (Next Week)
- Build feature engineering pipeline
- Train first XGBoost model
- Iterate on features and hyperparameters
- Achieve target metrics

**The fun part is coming - you're almost to model training!** 🎯

---

## Emergency Contact Info

If you get stuck tomorrow:

**Reference Materials:**
- Your project knowledge files (extensive!)
- sklearn documentation
- XGBoost documentation
- Basketball-Reference.com for NBA context

**Key Principles to Remember:**
1. Temporal integrity: only `_PRIOR` features
2. Four Factors drive 96% of variance
3. Net Rating Differential is strongest single predictor
4. Calibration > raw accuracy
5. Keep it simple first, add complexity later

---

## Final Checklist Before Bed Tonight

- [ ] This preparation document reviewed
- [ ] Tomorrow's schedule clear in mind
- [ ] Reference files bookmarked
- [ ] Work environment ready
- [ ] Get good sleep! 😴

**See you tomorrow at 8:00 AM for another productive day! 💪**

---

_Prepared: November 27, 2025, 6:00 PM_  
_For: Friday, November 28, 2025_  
_Status: Ready to execute_ ✅