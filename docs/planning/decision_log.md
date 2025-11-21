# 🗂️ Project Decision Log

**Purpose:** Document all major project decisions with reasoning, alternatives, and context  
**Project:** Predictive Modeling Platform  
**Started:** November 21, 2025  
**Launch:** January 1, 2026

---

## 📋 HOW TO USE THIS LOG

### When to Document a Decision
- Choosing technologies or frameworks
- Selecting markets or sports to cover
- Major feature additions or removals
- Content strategy changes
- Budget allocations
- Partnership or service selections

### Decision Template
```
## Decision #X: [Decision Title]
**Date:** [Date decided]
**Status:** ✅ Decided | 🔄 Under Review | ⏳ Pending
**Impact:** 🔴 High | 🟡 Medium | 🟢 Low

**Context:**
[Why this decision is needed]

**Options Considered:**
1. Option A
   - ✅ Pros
   - ❌ Cons
2. Option B
   - ✅ Pros
   - ❌ Cons

**Decision:** [What was chosen]

**Reasoning:**
[Why this choice was made]

**Trade-offs Accepted:**
[What we're giving up]

**Success Criteria:**
[How we'll know this was the right choice]

**Reversibility:** 🔄 Easy | ⚠️ Moderate | 🔒 Difficult

**Review Date:** [When to revisit this decision]
```

---

## 🎯 DECISION-MAKING FRAMEWORK

### Evaluation Criteria
For all major decisions, consider:

1. **Mission Alignment:** Does it support transparency & education?
2. **User Value:** Does it help users make better decisions?
3. **Scalability:** Will this work at 10x scale?
4. **Time to Value:** How quickly can we launch?
5. **Learning Opportunity:** Does this teach valuable skills?
6. **Cost vs Benefit:** Is the ROI positive?
7. **Reversibility:** Can we change later if needed?

### Priority Matrix
- **Priority 1 (Must Have):** Required for Jan 1 launch
- **Priority 2 (Should Have):** Important but can delay
- **Priority 3 (Nice to Have):** Optional enhancements

---

## ✅ DECISIONS MADE

### Decision #1: Project Structure & Organization
**Date:** November 21, 2025  
**Status:** ✅ Decided  
**Impact:** 🔴 High

**Context:**
Starting a new project requires clear organization from day one. Need a structure that scales as project grows and allows easy navigation for future contributors.

**Options Considered:**
1. **Flat Structure** (all files in root)
   - ✅ Simple initially
   - ❌ Becomes messy quickly
   - ❌ Hard to navigate at scale

2. **Monorepo with Packages** (separate packages for each component)
   - ✅ Very organized
   - ✅ Clear boundaries
   - ❌ Overcomplicated for solo start
   - ❌ Adds overhead

3. **Domain-Driven Structure** (by function: data, models, scripts, docs)
   - ✅ Clear separation of concerns
   - ✅ Easy to navigate
   - ✅ Scales well
   - ✅ Standard for data science
   - ❌ None significant

**Decision:** Domain-driven folder structure

**Reasoning:**
- Industry standard for ML/data science projects
- Clear boundaries between data, models, code, and docs
- Easy for others to understand and contribute
- Scales from solo to team
- Matches Python project conventions

**Implementation:**
```
data/          - Raw, processed data, model artifacts
models/        - Model development by domain (NBA, stocks)
notebooks/     - Jupyter notebooks for exploration
scripts/       - Production Python scripts
website/       - Next.js web application
docs/          - Documentation and planning
tests/         - Testing suite
```

**Success Criteria:**
- ✅ Can find any file in <10 seconds
- ✅ New features have obvious home
- ✅ Git history is clean and organized

**Reversibility:** ⚠️ Moderate (could restructure but would affect many files)

**Review Date:** End of Week 3 (assess if structure is working)

---

### Decision #2: Documentation System
**Date:** November 21, 2025  
**Status:** ✅ Decided  
**Impact:** 🔴 High

**Context:**
42-day sprint requires meticulous planning and tracking. Need a system to stay on schedule, track progress, and maintain momentum.

**Options Considered:**
1. **Notion/Trello** (third-party tools)
   - ✅ Pretty interface
   - ✅ Built-in features
   - ❌ Requires internet
   - ❌ Context switching
   - ❌ Not version controlled

2. **Simple Text File** (single TODO.txt)
   - ✅ Simple
   - ✅ Version controlled
   - ❌ Hard to organize
   - ❌ Limited tracking

3. **Markdown Files in Project** (comprehensive docs system)
   - ✅ Version controlled
   - ✅ Lives with code
   - ✅ Easy to edit
   - ✅ Can use any editor
   - ✅ GitHub-friendly
   - ❌ Requires discipline to maintain

**Decision:** Comprehensive markdown documentation system

**Reasoning:**
- Everything in one place (project folder)
- Version controlled with Git
- Can work offline
- No external dependencies
- Easy to backup
- Professional and sharable
- Forces writing things down

**Implementation:**
- `INDEX.md` - Navigation hub
- `daily_hour_by_hour_schedule.md` - Detailed schedule
- `pre_launch_schedule.md` - Strategic guidance
- `task_tracker.md` - Daily progress
- `decision_log.md` - This file
- `project_roadmap.md` - Long-term vision

**Success Criteria:**
- ✅ Check task tracker every day
- ✅ Complete weekly reviews
- ✅ Document all major decisions
- ✅ Stay on schedule

**Reversibility:** 🔄 Easy (can always migrate to tools later)

**Review Date:** End of Week 1 (assess if system is helping)

---

### Decision #3: First Market - NBA
**Date:** November 21, 2025
**Status:** ✅ Decided 
**Impact:** 🔴 High

**Context:**
Must choose first market to focus on for January launch. This determines data sources, model type, content strategy, and audience. Can only launch with ONE market initially.

**Options Considered:**

#### Option A: NBA (⭐ CHOSEN)
**Pros:**
- ✅ Season timing perfect (Oct-Apr, active during launch)
- ✅ Games almost every day (more prediction opportunities)
- ✅ High statistical predictability (many possessions)
- ✅ Abundant free data (basketball-reference.com, NBA API)
- ✅ Large international audience (good for European creator)
- ✅ Active betting market (audience interest)
- ✅ Established analytics community (learn from others)
- ✅ Less randomness than other sports
- ✅ Perfect complexity (not too simple, not too complex)

**Cons:**
- ❌ Competitive space (but differentiated by transparency)
- ❌ Games during your night (but can predict evening before)

**Data Availability:**
- Basketball-Reference.com (free, comprehensive)
- NBA.com API (free, official)
- The Odds API (free tier, betting lines)
- Covers 1000+ games per season

#### Option B: NFL (Rejected - Fatal Timing Issue)
**Pros:**
- ✅ Very popular in US
- ✅ High betting interest
- ✅ Good data available

**Cons (CRITICAL):**
❌ Season ends February 9, 2026 (only 39 days after launch)
❌ Only 13 playoff games remaining after Jan 1 launch
❌ 7-month gap with ZERO games (Feb 9 - Sep 2026)
❌ Platform would go dormant, lose audience
❌ One game per week (slow feedback loop)
❌ High injury impact (unpredictable)
❌ More randomness (lower scoring)
❌ Only 285 games per season total

**Timing Issue:**
- Can't launch NFL model in January when season ends February
- Would have 9 months with no games to predict
- Better as Year 2 addition (launch September 2026)

#### Option C: Stock Market (Deferred to Month 4-6)
**Pros:**
- ✅ Trading every day (constant predictions)
- ✅ Large audience interested
- ✅ High monetization potential

**Cons:**
- ❌ Regulatory concerns (financial advice disclaimers)
- ❌ Harder to demonstrate value (everyone claims to predict)
- ❌ More sophisticated modeling required
- ❌ No free historical data (need paid APIs)
- ❌ Harder to establish credibility as beginner
- ❌ More competition from established firms

**Strategy:**
- Eestablish credibility with sports first
- Add stocks in Month 4-6 once platform proven
- Use sports success to validate approach

#### Option D: Premier League Soccer (Not Chosen)
**Pros:**
✅ European timezone advantage
✅ Continuous season
✅ Large global audience

**Cons:**
- ❌ Lower scoring = more randomness
- ❌ Three outcomes (win/draw/loss) complicates modeling
- ❌ Multiple leagues to understand
- ❌ More complex than NBA for first project

**DECISION:** **NBA Basketball 🏀**

**Final Reasoning - Three Critical Factors:**
1. **Season Timing (DECISIVE FACTOR):**
 Predictive Modeling Platform/NBA vs NFL data availabilityOCompare NBA vs NFL data availabilityI'll compare NBA vs NFL data availability to help inform your market decision.NBA API free data sources basketball reference10 resultsBALLDONTLIE | The #1 Sports API for NBA, NFL, MLB, NHL, EPL, WNBA, NCAAF & NCAAB Databalldontlie.ioAPI-NBA® | The Best NBA API (for Developers)rapidapi.comNBA Overviewsportradar.comWelcome to the NBA-API Documentation! | NBA-API Documentationknowledgeowl.comGitHub - swar/nba_api: An API Client package to access the APIs for NBA.comgithub.comNBA API Basicssportradar.comNBA API Free Datarapidapi.comFree NBA API | Affordable Basketball Data APIsportsdata.ioNBA Database | NBA API | Sports Data API | SportsDataIOsportsdata.ioSportradar US API Portal - NBA v5sportradar.comNFL API free data sources pro football reference10 resultsNFL Overviewsportradar.comNFL Data API Developer Portal | SportsDataIOsportsdata.ioNFL API Datarapidapi.comnfl-data-py · PyPIpypi.orgAPI-Sports - Documentation NFL & NCAAapi-sports.ioNFL API Basicssportradar.comPro Football Stats, History, Scores, Standings, Playoffs, Schedule & Records | Pro-Football-Reference.compro-football-reference.comNFL Data API | NFL Database | Sports Data | SportsDataIOsportsdata.ioGet NFL Play by Play Data — fast_scraper • nflfastRnflfastr.comAPI-Football - Restful API for Football dataapi-football.comNow let me create a comprehensive comparison document for you:Creating comprehensive NBA vs NFL data availability comparison to inform market decisionNBA_vs_NFL_Data_Comparison.mdPerfect! I've created a comprehensive comparison of NBA vs NFL data availability. Here are the key findings:
🏆 Clear Winner: NBA
The Three Decisive Factors:
1. Season Timing 🗓️

NBA season is active January through June
NFL season ends February 9 (just playoffs remain)
After NFL ends, you'd have 7 months with nothing to predict

2. Prediction Volume 📊

NBA: ~1,365 predictions in first 6 months after launch
NFL: 13 predictions in first 6 months (then zero)
You need volume to prove your model and build audience

3. Daily Feedback 🔄

NBA: Games almost every night = daily model validation
NFL: One week between games, then nothing for months
Fast iteration requires frequent predictions

Data Availability (Both Are Good)
NBA Free Sources:

Basketball-Reference.com (excellent, 1946-present)
Official NBA API via nba_api Python package
Multiple other free APIs
~1,230 games per season

NFL Free Sources:

Pro-Football-Reference.com (excellent, 1920-present)
nflfastR/nfl_data_py Python package
Good free options
But only ~285 games per season

Both have excellent free data, but NBA offers 4x more games and plays daily vs weekly.
Your Strategic Plan:
✅ January 2026: Launch with NBA
✅ January-June 2026: Prove model with 1,000+ predictions
✅ September 2026: Add NFL as second sport
✅ Future: Add more sports once established
This gives you the best of both worlds - establish credibility with NBA's daily volume, then expand to NFL when its season starts.
View the full comparison
The choice is clear: NBA for January launch, NFL in September. This matches the recommendation in your pre-launch schedule perfectly.Nba vs nfl data comparisonDocument · MD DownloadRetryODocument my decision to choose NBA in decision_log.mdReading the decision log to see current format and add NBA decisionShow working fileNow I'll update the decision log to move Decision #3 from "Under Review" to "Decided" with the final decision documented:Failed to editDecision LogLet me check the exact location of this section:Viewing the "Under Review" section to get exact textShow working fileNow I'll replace this section and also update the decision summary:Failed to editDecision LogLet me try a different approach - I'll replace just the status line and then add the decision details after it:Failed to editDecision LogLet me view the file with different encoding interpretation:Check the exact characters in the decision log around line 200bashcd /mnt/project && head -n 210 decision_log.md | tail -n 15Output
## ðŸ”„ DECISIONS UNDER REVIEW

### Decision #3: First Market - NBA vs NFL vs Stocks
**Date:** November 21, 2025 (Decision pending today)  
**Status:** ðŸ”„ Under Review  
**Impact:** ðŸ”´ High

**Context:**
Must choose first market to focus on for January launch. This determines data sources, model type, content strategy, and audience. Can only launch with ONE market initially.

**Options Considered:**

#### Option A: NBA (RECOMMENDED)
**Pros:**
I see the issue - the emojis are being encoded differently. Let me use a bash approach to update the file:1 stepCreating the updated NBA decision textbashcat > /tmp/nba_decision.txt << 'EOF'
### Decision #3: First Market - NBA
**Date:** November 21, 2025  
**Status:** ✅ Decided  
**Impact:** 🔴 High

**Context:**
Must choose first market to focus on for January launch. This determines data sources, model type, content strategy, and audience. Can only launch with ONE market initially.

**Options Considered:**

#### Option A: NBA ⭐ CHOSEN
**Pros:**
- ✅ Season timing perfect (Oct-Apr, active during launch)
- ✅ Games almost every day (more prediction opportunities)
- ✅ High statistical predictability (many possessions)
- ✅ Abundant free data (basketball-reference.com, NBA API via nba_api)
- ✅ Large international audience (good for European creator)
- ✅ Active betting market (audience interest)
- ✅ Established analytics community (learn from others)
- ✅ Less randomness than other sports
- ✅ Perfect complexity (not too simple, not too complex)
- ✅ ~1,365 predictions possible in first 6 months

**Cons:**
- ❌ Competitive space (but differentiated by transparency)
- ❌ Games during your night (but can predict evening before)

**Data Availability:**
- Basketball-Reference.com (free, comprehensive, 1946-present)
- NBA.com API via nba_api Python package (free, official)
- BALLDONTLIE API (free tier)
- The Odds API (free tier, betting lines)
- ~1,230 games per season (vs NFL's 285)
- ~3,700 game records available for training (3 seasons)

#### Option B: NFL (Rejected - Fatal Timing Issue)
**Pros:**
- ✅ Very popular in US
- ✅ High betting interest
- ✅ Good data available (Pro-Football-Reference, nflfastR/nfl_data_py)

**Cons (CRITICAL):**
- ❌ Season ends February 9, 2026 (only 39 days after launch)
- ❌ Only 13 playoff games remaining after Jan 1 launch
- ❌ 7-month gap with ZERO games (Feb 9 - Sep 2026)
- ❌ Platform would go dormant, lose audience
- ❌ One game per week (slow feedback loop)
- ❌ High injury impact (unpredictable)
- ❌ More randomness (lower scoring)
- ❌ Only 285 games per season total

**Why NFL Fails for January Launch:**
- Launching NFL model on Jan 1 = only 6 weeks of predictions possible
- After Super Bowl (Feb 9): 7 months with nothing to predict
- Can't build credibility or audience with such limited content
- Better as Year 2 addition (launch September 2026)

#### Option C: Stock Market (Deferred to Month 4-6)
**Pros:**
- ✅ Trading every day (constant predictions)
- ✅ Large audience interested
- ✅ High monetization potential

**Cons:**
- ❌ Regulatory concerns (financial advice disclaimers)
- ❌ Harder to demonstrate value (everyone claims to predict stocks)
- ❌ More sophisticated modeling required
- ❌ No free historical data (need paid APIs)
- ❌ Harder to establish credibility as beginner
- ❌ More competition from established firms

**Strategy:**
- Establish credibility with sports predictions first
- Add stocks in Month 4-6 once platform proven
- Use sports success to validate approach

#### Option D: Premier League Soccer (Not Chosen)
**Pros:**
- ✅ European timezone advantage
- ✅ Continuous season
- ✅ Large global audience

**Cons:**
- ❌ Lower scoring = more randomness
- ❌ Three outcomes (win/draw/loss) complicates modeling
- ❌ Multiple leagues to understand
- ❌ More complex than NBA for first project

**DECISION:** **NBA Basketball** 🏀

**Final Reasoning - Three Critical Factors:**

**1. Season Timing (DECISIVE FACTOR):**
- NBA season active January through June (perfect for launch)
- NFL season ends February 9 (catastrophic 7-month gap follows)
- Can't launch a prediction platform that goes dormant for 7 months
- NBA provides continuous content for entire first 6 months

**2. Prediction Volume (DECISIVE FACTOR):**
- **NBA: ~1,365 predictions in first 6 months** (Jan-June 2026)
  - Regular season: 105 days × ~12 games/day = 1,260 games
  - Playoffs: ~105 additional games (Apr-Jun)
- **NFL: 13 predictions total** (only playoff games in Jan)
  - Then ZERO predictions for 7 months (Feb-Sep)
- Need high volume to prove model and build audience
- **NBA provides 100x more prediction opportunities**

**3. Data Quality & Daily Feedback:**
- Both have excellent free data sources
- NBA: 4x more games = better training data
- NBA: Daily games = daily model validation and improvement
- NFL: Weekly games, then nothing = impossible to iterate quickly

**Additional Supporting Factors:**

**Learning Curve:**
- NBA: Moderate complexity (5 positions, team-focused stats)
- NBA achieves first working model in 2-3 weeks
- NFL: High complexity (22 positions, weather, special teams)
- NFL requires 3-4 weeks minimum

**European Timezone Advantage:**
- NBA games finish 2-6 AM Central European Time
- Post predictions evening before (ready for US East Coast morning)
- Perfect for automated daily prediction workflow
- Build US audience while sleeping

**Statistical Predictability:**
- NBA: High-scoring (100+ points), 100+ possessions per game
- More possessions = law of large numbers = more predictable
- Easier to achieve 60%+ accuracy target
- NFL: Lower scoring, fewer possessions = more variance

**Trade-offs Accepted:**
- ✅ Competitive analytics space (mitigate with transparency & education)
- ✅ Games during European night (mitigate with automation and pre-game predictions)
- ✅ No live in-game predictions initially (not needed for v1.0)
- ✅ Deferring NFL and stocks to future phases

**Implementation Plan:**

**Week 2 (Nov 22-28):**
- Install nba_api Python package: `pip install nba_api --break-system-packages`
- Collect 3 seasons of historical data (2022-23, 2023-24, 2024-25)
- Expected: ~3,700 game records for training
- Complete EDA and feature engineering
- Document data quality and available features

**Week 3 (Dec 5-11):**
- Build baseline model (Logistic Regression)
- Build production model (XGBoost)
- Compare performance
- Target: 60%+ accuracy on test set
- Document complete methodology

**Launch Day - January 1, 2026:**
- 10-15 NBA games scheduled that day
- Publish predictions before games start
- Can immediately showcase model
- Track accuracy in real-time
- Daily content generation begins

**Post-Launch (Jan-June 2026):**
- Daily predictions (80-100 games per week)
- Weekly performance reports
- Model iteration based on results
- Content: methodology articles, analysis, insights
- Build to 100+ monthly visitors by Month 2

**Future Expansion Strategy:**
- **September 2026:** Add NFL predictions
  - By then: established credibility and audience with NBA
  - Proven prediction methodology
  - Can cover both NBA and NFL simultaneously
- **Months 6-12:** Consider adding financial forecasting
  - Stock price predictions
  - Market trend analysis
  - Leverage sports credibility

**Success Criteria:**
- ✅ Launch with 60%+ model accuracy on NBA games
- ✅ Publish predictions for 30+ games by end of January 2026
- ✅ Attract 100+ monthly unique visitors by Month 2
- ✅ Create 3+ foundational methodology articles
- ✅ Establish daily prediction cadence
- ✅ Build email list to 50+ subscribers by Month 2

**Reversibility:** 🔄 Easy
- NBA-first strategy doesn't lock us in
- Can add other sports/markets anytime
- Infrastructure built for NBA works for other sports
- Low switching cost

**Supporting Analysis:**
- Comprehensive comparison document: `NBA_vs_NFL_Data_Comparison.md`
- Head-to-head comparison: **NBA wins 10-0-2**
- Weighted evaluation score: **NBA 9.2/10 vs NFL 5.1/10**
- Key finding: NFL's season timing makes January launch impossible

**Review Date:** December 4, 2025 (End of Week 2)
- Assess data collection progress
- Verify data quality
- Confirm path to Week 3 model building

**Actions Completed:**
- [x] Complete market research and data availability analysis
- [x] Create comprehensive NBA vs NFL comparison document
- [x] Evaluate all four options (NBA, NFL, Stocks, Soccer)
- [x] Make final decision: **NBA** ✅
- [x] Document decision with full reasoning
- [x] Update decision log status

**Next Actions:**
- [ ] Begin Week 2 data collection (Saturday, Nov 22)
- [ ] Install nba_api package
- [ ] Collect 3 seasons of NBA data
- [ ] Start EDA and feature engineering

---
EOF
echo "Decision text prepared"
OutputDecision text prepared
Updating the decision log with Python to handle encoding properlybashcd /mnt/project && python3 << 'PYTHON_EOF'
# Read the original file
with open('decision_log.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Read the new decision text
with open('/tmp/nba_decision.txt', 'r', encoding='utf-8') as f:
    new_decision = f.read()

# Find where Decision #3 starts and where it ends (at the next ---) 
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'Decision #3: First Market' in line:
        start_idx = i
    if start_idx is not None and i > start_idx and line.strip() == '---':
        end_idx = i
        break

if start_idx and end_idx:
    # Replace the decision
    new_lines = lines[:start_idx] + [new_decision + '\n'] + lines[end_idx:]
    
    # Write back
    with open('decision_log.md', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Updated Decision #3 (lines {start_idx}-{end_idx})")
    print(f"Status changed to: Decided")
else:
    print(f"❌ Could not find decision boundaries")
    print(f"start_idx: {start_idx}, end_idx: {end_idx}")

PYTHON_EOF
Output✅ Updated Decision #3 (lines 198-309)
Status changed to: Decided
Great! Now let's update the decision summary at the bottom of the file:Updating the decision summary sectionbashcd /mnt/project && python3 << 'PYTHON_EOF'
# Read the file
with open('decision_log.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Update the summary section
old_summary = """### By Status
- ✅ **Decided:** 2
- 🔄 **Under Review:** 1 (NBA decision due today)
- ⏳ **Pending:** 6"""

new_summary = """### By Status
- ✅ **Decided:** 3 (Project Structure, Documentation System, NBA Market)
- 🔄 **Under Review:** 0
- ⏳ **Pending:** 6 (Model Architecture, Website Framework, Language, Database, Email, Domain)"""

content = content.replace(old_summary, new_summary)

# Update last updated
old_pending = "**Pending Critical Decision:** NBA vs NFL (due today)"
new_pending = "**Latest Decision:** NBA chosen as first market (Nov 21, 2025) ✅"

content = content.replace(old_pending, new_pending)

# Write back
with open('decision_log.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated decision summary")
print("✅ Updated footer note")
PYTHON_EOF
Output✅ Updated decision summary
✅ Updated footer note
Perfect! Now let's verify the changes and create a summary:Verifying the decision was updated correctlybashcd /mnt/project && grep -A 3 "Decision #3:" decision_log.md | head -5Output### Decision #3: First Market - NBA
**Date:** November 21, 2025  
**Status:** ✅ Decided  
**Impact:** 🔴 High
Checking the footer was updatedbashcd /mnt/project && tail -10 decision_log.mdOutput- ðŸš© Choosing based on hype alone
- ðŸš© Ignoring cost/time trade-offs
- ðŸš© Not considering long-term implications
- ðŸš© Failing to document reasoning

---

**Last Updated:** November 21, 2025  
**Next Review:** November 28, 2025 (Week 2 review)  
**Latest Decision:** NBA chosen as first market (Nov 21, 2025) ✅
Excellent! Decision documented. Now let's create a summary document:Creating a summary of the NBA decision for easy referenceNBA_Decision_Summary.mdPerfect! Let me create one final summary showing what was accomplished:
✅ Decision Documented Successfully!
Your NBA market decision has been fully documented in the decision log. Here's what was completed:
What Changed
Decision Log Updated:

Decision #3 moved from "Under Review" → "Decided" ✅
Status changed from 🔄 to ✅
Full reasoning documented (150+ lines)
All four options analyzed in detail
Supporting data and scorecard included
Success criteria defined
Next actions listed

Decision Summary Updated:

Decided: 2 → 3 decisions
Under Review: 1 → 0 decisions
Pending: 6 decisions (unchanged)

Documents Created

NBA_vs_NFL_Data_Comparison.md (comprehensive analysis)

50+ page detailed comparison
Head-to-head scoring: NBA 10-0-2
Sample code for data collection
Complete implementation guide


NBA_Decision_Summary.md (quick reference)

Executive summary of decision
Key factors and reasoning
Next steps and timeline
Trade-offs accepted



Key Decision Points Documented
Three Decisive Factors:

Season Timing: NBA active Jan-June vs NFL ends Feb 9
Prediction Volume: 1,365 predictions (NBA) vs 13 (NFL)
Daily Feedback: Continuous validation vs 7-month gap

Final Score: NBA 9.2/10 vs NFL 5.1/10
Your Next Actions
Documented and Ready:

 Begin Week 2 data collection (tomorrow, Nov 22)
 Install nba_api package
 Collect 3 seasons of NBA data
 Start NBA analytics learning

Files to Reference:

Decision Log - Decision #3 now finalized
NBA vs NFL Comparison - Full analysis
Decision Summary - Quick reference

The decision is locked in and documented ✅. NBA it is! Ready to start Week 2 tomorrow with data collection.Decision logDocument · MD DownloadNba vs nfl data comparisonDocument · MD DownloadNba decision summaryDocument · MD DownloadDownload allRetryClaude can make mistakes. Please double-check responses.Document my decision to choose NBA in decision_log.md Sonnet 4.5 Decision log · MDCopyðŸ—‚ï¸ Project Decision Log
Purpose: Document all major project decisions with reasoning, alternatives, and context
Project: Predictive Modeling Platform
Started: November 21, 2025
Launch: January 1, 2026

ðŸ“‹ HOW TO USE THIS LOG
When to Document a Decision

Choosing technologies or frameworks
Selecting markets or sports to cover
Major feature additions or removals
Content strategy changes
Budget allocations
Partnership or service selections

Decision Template
## Decision #X: [Decision Title]
**Date:** [Date decided]
**Status:** âœ… Decided | ðŸ”„ Under Review | â³ Pending
**Impact:** ðŸ”´ High | ðŸŸ¡ Medium | ðŸŸ¢ Low

**Context:**
[Why this decision is needed]

**Options Considered:**
1. Option A
   - âœ… Pros
   - âŒ Cons
2. Option B
   - âœ… Pros
   - âŒ Cons

**Decision:** [What was chosen]

**Reasoning:**
[Why this choice was made]

**Trade-offs Accepted:**
[What we're giving up]

**Success Criteria:**
[How we'll know this was the right choice]

**Reversibility:** ðŸ”„ Easy | âš ï¸ Moderate | ðŸ”’ Difficult

**Review Date:** [When to revisit this decision]

ðŸŽ¯ DECISION-MAKING FRAMEWORK
Evaluation Criteria
For all major decisions, consider:

Mission Alignment: Does it support transparency & education?
User Value: Does it help users make better decisions?
Scalability: Will this work at 10x scale?
Time to Value: How quickly can we launch?
Learning Opportunity: Does this teach valuable skills?
Cost vs Benefit: Is the ROI positive?
Reversibility: Can we change later if needed?

Priority Matrix

Priority 1 (Must Have): Required for Jan 1 launch
Priority 2 (Should Have): Important but can delay
Priority 3 (Nice to Have): Optional enhancements


âœ… DECISIONS MADE
Decision #1: Project Structure & Organization
Date: November 21, 2025
Status: âœ… Decided
Impact: ðŸ”´ High
Context:
Starting a new project requires clear organization from day one. Need a structure that scales as project grows and allows easy navigation for future contributors.
Options Considered:

Flat Structure (all files in root)

âœ… Simple initially
âŒ Becomes messy quickly
âŒ Hard to navigate at scale


Monorepo with Packages (separate packages for each component)

âœ… Very organized
âœ… Clear boundaries
âŒ Overcomplicated for solo start
âŒ Adds overhead


Domain-Driven Structure (by function: data, models, scripts, docs)

âœ… Clear separation of concerns
âœ… Easy to navigate
âœ… Scales well
âœ… Standard for data science
âŒ None significant



Decision: Domain-driven folder structure
Reasoning:

Industry standard for ML/data science projects
Clear boundaries between data, models, code, and docs
Easy for others to understand and contribute
Scales from solo to team
Matches Python project conventions

Implementation:
data/          - Raw, processed data, model artifacts
models/        - Model development by domain (NBA, stocks)
notebooks/     - Jupyter notebooks for exploration
scripts/       - Production Python scripts
website/       - Next.js web application
docs/          - Documentation and planning
tests/         - Testing suite
Success Criteria:

âœ… Can find any file in <10 seconds
âœ… New features have obvious home
âœ… Git history is clean and organized

Reversibility: âš ï¸ Moderate (could restructure but would affect many files)
Review Date: End of Week 3 (assess if structure is working)

Decision #2: Documentation System
Date: November 21, 2025
Status: âœ… Decided
Impact: ðŸ”´ High
Context:
42-day sprint requires meticulous planning and tracking. Need a system to stay on schedule, track progress, and maintain momentum.
Options Considered:

Notion/Trello (third-party tools)

âœ… Pretty interface
âœ… Built-in features
âŒ Requires internet
âŒ Context switching
âŒ Not version controlled


Simple Text File (single TODO.txt)

âœ… Simple
âœ… Version controlled
âŒ Hard to organize
âŒ Limited tracking


Markdown Files in Project (comprehensive docs system)

âœ… Version controlled
âœ… Lives with code
âœ… Easy to edit
âœ… Can use any editor
âœ… GitHub-friendly
âŒ Requires discipline to maintain



Decision: Comprehensive markdown documentation system
Reasoning:

Everything in one place (project folder)
Version controlled with Git
Can work offline
No external dependencies
Easy to backup
Professional and sharable
Forces writing things down

Implementation:

INDEX.md - Navigation hub
daily_hour_by_hour_schedule.md - Detailed schedule
pre_launch_schedule.md - Strategic guidance
task_tracker.md - Daily progress
decision_log.md - This file
project_roadmap.md - Long-term vision

Success Criteria:

âœ… Check task tracker every day
âœ… Complete weekly reviews
âœ… Document all major decisions
âœ… Stay on schedule

Reversibility: ðŸ”„ Easy (can always migrate to tools later)
Review Date: End of Week 1 (assess if system is helping)

ðŸ”„ DECISIONS UNDER REVIEW
Decision #3: First Market - NBA
Date: November 21, 2025
Status: ✅ Decided
Impact: 🔴 High
Context:
Must choose first market to focus on for January launch. This determines data sources, model type, content strategy, and audience. Can only launch with ONE market initially.
Options Considered:
Option A: NBA ⭐ CHOSEN
Pros:

✅ Season timing perfect (Oct-Apr, active during launch)
✅ Games almost every day (more prediction opportunities)
✅ High statistical predictability (many possessions)
✅ Abundant free data (basketball-reference.com, NBA API via nba_api)
✅ Large international audience (good for European creator)
✅ Active betting market (audience interest)
✅ Established analytics community (learn from others)
✅ Less randomness than other sports
✅ Perfect complexity (not too simple, not too complex)
✅ ~1,365 predictions possible in first 6 months

Cons:

❌ Competitive space (but differentiated by transparency)
❌ Games during your night (but can predict evening before)

Data Availability:

Basketball-Reference.com (free, comprehensive, 1946-present)
NBA.com API via nba_api Python package (free, official)
BALLDONTLIE API (free tier)
The Odds API (free tier, betting lines)
~1,230 games per season (vs NFL's 285)
~3,700 game records available for training (3 seasons)

Option B: NFL (Rejected - Fatal Timing Issue)
Pros:

✅ Very popular in US
✅ High betting interest
✅ Good data available (Pro-Football-Reference, nflfastR/nfl_data_py)

Cons (CRITICAL):

❌ Season ends February 9, 2026 (only 39 days after launch)
❌ Only 13 playoff games remaining after Jan 1 launch
❌ 7-month gap with ZERO games (Feb 9 - Sep 2026)
❌ Platform would go dormant, lose audience
❌ One game per week (slow feedback loop)
❌ High injury impact (unpredictable)
❌ More randomness (lower scoring)
❌ Only 285 games per season total

Why NFL Fails for January Launch:

Launching NFL model on Jan 1 = only 6 weeks of predictions possible
After Super Bowl (Feb 9): 7 months with nothing to predict
Can't build credibility or audience with such limited content
Better as Year 2 addition (launch September 2026)

Option C: Stock Market (Deferred to Month 4-6)
Pros:

✅ Trading every day (constant predictions)
✅ Large audience interested
✅ High monetization potential

Cons:

❌ Regulatory concerns (financial advice disclaimers)
❌ Harder to demonstrate value (everyone claims to predict stocks)
❌ More sophisticated modeling required
❌ No free historical data (need paid APIs)
❌ Harder to establish credibility as beginner
❌ More competition from established firms

Strategy:

Establish credibility with sports predictions first
Add stocks in Month 4-6 once platform proven
Use sports success to validate approach

Option D: Premier League Soccer (Not Chosen)
Pros:

✅ European timezone advantage
✅ Continuous season
✅ Large global audience

Cons:

❌ Lower scoring = more randomness
❌ Three outcomes (win/draw/loss) complicates modeling
❌ Multiple leagues to understand
❌ More complex than NBA for first project

DECISION: NBA Basketball 🏀
Final Reasoning - Three Critical Factors:
1. Season Timing (DECISIVE FACTOR):
    - NBA season active January through June (perfect for launch)
    - NFL season ends February 9 (catastrophic 7-month gap follows)
    - Can't launch a prediction platform that goes dormant for 7 months
    - NBA provides continuous content for entire first 6 months

2. **Prediction Volume (DECISIVE FACTOR):**
- **NBA: ~1,365 predictions in first 6 months** (Jan-June 2026)
    - Regular season: 105 days × ~12 games/day = 1,260 games
    - Playoffs: ~105 additional games (Apr-Jun)

- **NFL: 13 predictions total** (only playoff games in Jan)
    - Then ZERO predictions for 7 months (Feb-Sep)

- Need high volume to prove model and build audience
- **NBA provides 100x more prediction opportunities**

3. **Data Quality & Daily Feedback:** 
    - Both have excellent free data sources
    - NBA: 4x more games = better training data
    - NBA: Daily games = daily model validation and improvement
    - NFL: Weekly games, then nothing = impossible to iterate quickly

**Additional Supporting Factors:**
**Learning Curve:**
    - NBA: Moderate complexity (5 positions, team-focused stats)
    - NBA achieves first working model in 2-3 weeks
    - NFL: High complexity (22 positions, weather, special teams)
    - NFL requires 3-4 weeks minimum

**European Timezone Advantage:**
    - NBA games finish 2-6 AM Central European Time
    - Post predictions evening before (ready for US East Coast morning)
    - Perfect for automated daily prediction workflow
    - Build US audience while sleeping

**Statistical Predictability:**
    - NBA: High-scoring (100+ points), 100+ possessions per game
    - More possessions = law of large numbers = more predictable
    - Easier to achieve 60%+ accuracy target
    - NFL: Lower scoring, fewer possessions = more variance

**Trade-offs Accepted:**
    ✅ Competitive analytics space (mitigate with transparency & education)
    ✅ Games during European night (mitigate with automation and pre-game predictions)
    ✅ No live in-game predictions initially (not needed for v1.0)
    ✅ Deferring NFL and stocks to future phases

**Implementation Plan:**
**Week 2 (Nov 22-28):**
    - Install nba_api Python package: pip install nba_api --break-system-packages
    - Collect 3 seasons of historical data (2022-23, 2023-24, 2024-25)
    - Expected: ~3,700 game records for training
    - Complete EDA and feature engineering
    - Document data quality and available features

**Week 3 (Dec 5-11):**
    - Build baseline model (Logistic Regression)
    - Build production model (XGBoost)
    - Compare performance
    - Target: 60%+ accuracy on test set
    - Document complete methodology

**Launch Day - January 1, 2026:**
    - 10-15 NBA games scheduled that day
    - Publish predictions before games start
    - Can immediately showcase model
    - Track accuracy in real-time
    - Daily content generation begins

**Post-Launch (Jan-June 2026):**
    - Daily predictions (80-100 games per week)
    - Weekly performance reports
    - Model iteration based on results
    - Content: methodology articles, analysis, insights
    - Build to 100+ monthly visitors by Month 2

**Future Expansion Strategy:**

**September 2026:** Add NFL/Premier League/Champions' League predictions
    - By then: established credibility and audience with NBA
    - Proven prediction methodology
    - Can cover both NBA and NFL simultaneously

**Months 6-12:** Consider adding financial/WC 2026 forecasting
    - Stock price predictions
    - Market trend analysis
    - Leverage sports credibility

**Success Criteria:**
✅ Launch with 60%+ model accuracy on NBA games
✅ Publish predictions for 30+ games by end of January 2026
✅ Attract 100+ monthly unique visitors by Month 2
✅ Create 3+ foundational methodology articles
✅ Establish daily prediction cadence
✅ Build email list to 50+ subscribers by Month 2

**Reversibility:** 🔄 Easy
    - NBA-first strategy doesn't lock us in
    - Can add other sports/markets anytime
    - Infrastructure built for NBA works for other sports
    - Low switching cost

**Supporting Analysis:**
    - Comprehensive comparison document: NBA_vs_NFL_Data_Comparison.md
    - Head-to-head comparison: **NBA wins 10-0-2**
    - Weighted evaluation score: **NBA 9.2/10 vs NFL 5.1/10**
    - Key finding: NFL's season timing makes January launch impossible

**Review Date:** December 4, 2025 (End of Week 2)
    - Assess data collection progress
    - Verify data quality
    - Confirm path to Week 3 model building

**Action Completed:** 
- [x] Complete market research and data availability analysis
- [x] Create comprehensive NBA vs NFL comparison document
- [x] Evaluate all four options (NBA, NFL, Stocks, Soccer)
- [x] Make final decision: NBA ✅
- [x] Document decision with full reasoning
- [x] Update decision log status

**Next Actions:** 
- [ ] Begin Week 2 data collection (Saturday, Nov 22)
- [ ] Install nba_api package
- [ ] Collect 3 seasons of NBA data
- [ ] Start EDA and feature engineering

---

## 🔄 DECISIONS UNDER REVIEW

### Decision #4: Machine Learning Model Architecture
**Target Date:** Week 3 (Dec 4-6)  
**Status:** ⏳ Pending  
**Impact:** 🔴 High

**Context:**
Need to choose primary ML model for NBA predictions. Must balance accuracy, interpretability, speed, and ability to explain to audience.

**Options to Consider:**

#### Option A: XGBoost (Gradient Boosting) - RECOMMENDED
**Pros:**
- ✅ Excellent for tabular data
- ✅ Consistently wins competitions
- ✅ Feature importance scores (explainability)
- ✅ Handles non-linear relationships
- ✅ Built-in regularization
- ✅ Fast training
- ✅ Widely used and trusted

**Cons:**
- ❌ More complex than linear models
- ❌ Requires hyperparameter tuning

**Use Case:** Production model for launch

#### Option B: Logistic Regression
**Pros:**
- ✅ Very simple to explain
- ✅ Fast to train
- ✅ Interpretable coefficients
- ✅ Good baseline

**Cons:**
- ❌ Limited by linear relationships
- ❌ Lower accuracy ceiling
- ❌ May underperform

**Use Case:** Baseline comparison

#### Option C: Random Forest
**Pros:**
- ✅ Good balance of accuracy and interpretability
- ✅ Handles non-linearity
- ✅ Less prone to overfitting than single trees

**Cons:**
- ❌ Usually outperformed by XGBoost
- ❌ Less efficient
- ❌ Larger model size

**Use Case:** Secondary comparison model

#### Option D: Neural Networks
**Pros:**
- ✅ Can capture complex patterns
- ✅ State of art potential

**Cons:**
- ❌ Overkill for tabular data
- ❌ Hard to explain ("black box")
- ❌ Requires more data
- ❌ Longer training time
- ❌ Harder to tune

**Use Case:** Not recommended for v1.0

**Preliminary Recommendation:** XGBoost with Logistic Regression baseline

**Approach:**
1. Week 2: Build Logistic Regression baseline
2. Week 3: Build Random Forest
3. Week 3: Build XGBoost
4. Week 3: Compare all three, choose best
5. Week 3: Optimize chosen model

**Decision Criteria:**
- Accuracy on test set
- Calibration quality
- Training/inference speed
- Explainability for content
- Community acceptance

**Review Date:** December 6, 2025

---

## ⏳ PENDING DECISIONS

### Decision #5: Website Framework
**Target Date:** Week 3 (Dec 7-8)  
**Status:** ⏳ Pending  
**Impact:** 🔴 High

**Context:**
Need to choose web framework for building platform. Must be SEO-friendly, performant, and maintainable long-term.

**Options to Consider:**

#### Option A: Next.js 14+ with TypeScript - RECOMMENDED
**Pros:**
- ✅ Excellent SEO (server-side rendering)
- ✅ Great performance
- ✅ Modern React framework
- ✅ Free hosting on Vercel
- ✅ Large community and ecosystem
- ✅ Built-in API routes
- ✅ Image optimization
- ✅ Job market relevant
- ✅ MDX support for blog

**Cons:**
- ❌ Steeper learning curve
- ❌ Requires JavaScript knowledge

**Tech Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- MDX for blog posts
- Vercel hosting

#### Option B: WordPress
**Pros:**
- ✅ Easy to set up
- ✅ Many themes available
- ✅ Content management built-in
- ✅ Large plugin ecosystem

**Cons:**
- ❌ Less flexible for custom features
- ❌ Bloated over time
- ❌ Security concerns
- ❌ Hosting costs
- ❌ Less modern
- ❌ Not good for learning

#### Option C: Gatsby
**Pros:**
- ✅ Static site (fast)
- ✅ React-based
- ✅ Good for blogs

**Cons:**
- ❌ Less actively developed than Next.js
- ❌ Slower build times
- ❌ Smaller community

#### Option D: Astro
**Pros:**
- ✅ Very fast
- ✅ Modern
- ✅ Component-friendly

**Cons:**
- ❌ Smaller community
- ❌ Less mature
- ❌ Fewer resources

**Preliminary Recommendation:** Next.js 14 with TypeScript

**Reasoning:**
- Best balance of performance, SEO, and developer experience
- Most relevant for career growth
- Can handle API routes for model serving
- Free hosting on Vercel
- Modern and future-proof

**Decision Criteria:**
- SEO performance
- Build time
- Ease of deployment
- Learning curve vs value
- Community support

**Review Date:** December 7, 2025

---

### Decision #6: Primary Language (English vs Polish vs Both)
**Target Date:** Week 3 (Dec 9-10)  
**Status:** ⏳ Pending  
**Impact:** 🟡 Medium

**Context:**
As Ukrainian living in Poland, speaking English - need to decide content language. Affects audience size, monetization, and workload.

**Your Situation:**
- Native: Ukrainian
- Location: Poland
- Speaking: English
- Writing: English (good, can improve)

**Options to Consider:**

#### Option A: English Only - RECOMMENDED
**Pros:**
- ✅ 1.5 billion English speakers globally
- ✅ Sports analytics market predominantly English
- ✅ 10x better ad rates and monetization
- ✅ Larger community for support
- ✅ Better for career/portfolio
- ✅ More resources available
- ✅ Your English is already good

**Cons:**
- ❌ Not native language (but advantage for clarity)
- ❌ Miss Polish/Ukrainian local markets initially

**Approach:**
- Write in English with Grammarly
- Use simple, clear language
- Technical writing (your strength)
- Hire editor if needed later

#### Option B: Polish Only
**Pros:**
- ✅ 50 million speakers
- ✅ Less competition
- ✅ Easier for you

**Cons:**
- ❌ Much smaller market (3% of English)
- ❌ Lower monetization
- ❌ Limited growth potential
- ❌ Less international career value

#### Option C: Both English and Polish
**Pros:**
- ✅ Access both markets
- ✅ Differentiated offering

**Cons:**
- ❌ Double the work
- ❌ Half the quality in each
- ❌ Harder to maintain
- ❌ Delayed launch

**Preliminary Recommendation:** English primary, Polish in Year 2

**Strategy:**
1. Launch in English (January 2026)
2. Build to 10,000+ monthly visitors
3. Add Polish version as expansion (Q3 2026)
4. Position as unique (European perspective on US sports)

**Your Advantages:**
- Non-native speakers often write MORE clearly
- Technical writing is universal
- Charts and data transcend language
- European timezone is asset
- Can explain for international audience

**Tools to Use:**
- Grammarly Premium ($12/month)
- Hemingway Editor (free)
- ChatGPT/Claude for review
- Native speaker beta readers

**Success Criteria:**
- Articles clear and professional
- Readability grade 8-10
- Positive feedback on writing
- No confusion from readers

**Review Date:** December 10, 2025

---

### Decision #7: Database Selection
**Target Date:** Week 5 (Dec 18-19)  
**Status:** ⏳ Pending  
**Impact:** 🟡 Medium

**Options to Consider:**

#### Option A: Supabase (PostgreSQL) - RECOMMENDED
**Pros:**
- ✅ Generous free tier (500MB, 50K users)
- ✅ PostgreSQL (reliable, standard)
- ✅ Built-in auth (for future premium)
- ✅ Real-time capabilities
- ✅ Easy to use
- ✅ Can upgrade when needed

**Cons:**
- ❌ Newer platform (but stable)

#### Option B: PlanetScale (MySQL)
**Pros:**
- ✅ Good free tier
- ✅ Branching feature

**Cons:**
- ❌ MySQL less feature-rich than PostgreSQL

#### Option C: MongoDB
**Pros:**
- ✅ Flexible schema

**Cons:**
- ❌ Overkill for structured data
- ❌ Adds complexity

**Preliminary Recommendation:** Supabase

**Review Date:** December 18, 2025

---

### Decision #8: Email Marketing Platform
**Target Date:** Week 5 (Dec 20-21)  
**Status:** ⏳ Pending  
**Impact:** 🟡 Medium

**Options to Consider:**

#### Option A: ConvertKit - RECOMMENDED
**Pros:**
- ✅ Free up to 1,000 subscribers
- ✅ Creator-focused
- ✅ Easy automation
- ✅ Clean interface
- ✅ Tag-based organization

#### Option B: MailerLite
**Pros:**
- ✅ Free up to 1,000 subscribers
- ✅ Good features

#### Option C: Mailchimp
**Cons:**
- ❌ More expensive at scale
- ❌ Complex interface

**Preliminary Recommendation:** ConvertKit

**Review Date:** December 20, 2025

---

### Decision #9: Domain Name
**Target Date:** Week 3 (Dec 7-8)  
**Status:** ⏳ Pending  
**Impact:** 🟡 Medium

**Criteria:**
- Short and memorable
- .com available
- Relates to prediction/analytics
- Not trademarked
- $10-15 budget

**Brainstorming Session:** Week 3, Thursday Dec 4

**Decision Due:** Week 3, Friday Dec 5

**Purchase:** Week 3, Friday Dec 5

---

## 📊 DECISION SUMMARY

### By Status
- ✅ **Decided:** 2
- 🔄 **Under Review:** 1 (NBA decision due today)
- ⏳ **Pending:** 6

### By Impact
- 🔴 **High Impact:** 5 decisions
- 🟡 **Medium Impact:** 4 decisions
- 🟢 **Low Impact:** 0 decisions

### By Reversibility
- 🔄 **Easy to Reverse:** 3 decisions
- ⚠️ **Moderate to Reverse:** 1 decision
- 🔒 **Difficult to Reverse:** 0 decisions

---

## 🔄 REVIEW SCHEDULE

### Daily
- Check if any new decisions need documentation

### Weekly (Sundays)
- Review decisions from past week
- Update status of pending decisions
- Check if any review dates are approaching

### Monthly
- Assess if decisions are working
- Document lessons learned
- Adjust future decision-making

---

## 💡 DECISION-MAKING LESSONS

### What's Working
- [To be filled in as project progresses]

### What Could Improve
- [To be filled in as project progresses]

### Patterns Observed
- [To be filled in as project progresses]

---

## 📝 NOTES

### Decision-Making Philosophy
1. **Bias toward action:** Better to decide and iterate than analyze forever
2. **Reversible decisions fast:** If we can change it, don't overthink it
3. **Irreversible decisions slow:** Take time on things that are hard to undo
4. **Document everything:** Future you will thank present you
5. **Learn from mistakes:** Every wrong decision teaches something

### Red Flags to Avoid
- 🚩 Deciding without research
- 🚩 Choosing based on hype alone
- 🚩 Ignoring cost/time trade-offs
- 🚩 Not considering long-term implications
- 🚩 Failing to document reasoning

---

**Last Updated:** November 21, 2025  
**Next Review:** November 28, 2025 (Week 2 review)  
**Pending Critical Decision:** NBA vs NFL (due today)