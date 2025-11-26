"""
Project Organization Script
============================

This script organizes your NBA prediction project into a clean, professional structure
suitable for GitHub and collaboration.

Run this script from your project root directory to:
1. Create proper directory structure
2. Move files to appropriate locations
3. Generate .gitignore
4. Create README.md
5. Generate requirements.txt

Location: scripts/utils/organize_project.py
"""

import os
import shutil
from pathlib import Path
import subprocess


class ProjectOrganizer:
    """Organize project files into proper structure."""
    
    def __init__(self, project_root: str = "."):
        self.root = Path(project_root).resolve()
        self.structure = {
            'data': ['raw', 'processed', 'external'],
            'scripts': ['data_collection', 'data_processing', 'exploratory', 'modeling', 'utils'],
            'models': [],
            'notebooks': [],
            'docs': ['technical', 'research', 'planning'],
            'tests': [],
            'outputs': ['figures', 'reports', 'predictions'],
        }
        
    def create_directory_structure(self):
        """Create all necessary directories."""
        print("\n" + "="*80)
        print("CREATING DIRECTORY STRUCTURE")
        print("="*80 + "\n")
        
        for main_dir, subdirs in self.structure.items():
            main_path = self.root / main_dir
            main_path.mkdir(exist_ok=True)
            print(f"✓ Created: {main_dir}/")
            
            for subdir in subdirs:
                sub_path = main_path / subdir
                sub_path.mkdir(exist_ok=True)
                print(f"  ✓ Created: {main_dir}/{subdir}/")
                
                # Create .gitkeep for empty directories
                gitkeep = sub_path / '.gitkeep'
                gitkeep.touch()
    
    def organize_documentation_files(self):
        """Move documentation files to docs/ directory."""
        print("\n" + "="*80)
        print("ORGANIZING DOCUMENTATION")
        print("="*80 + "\n")
        
        # Technical documentation
        technical_docs = {
            'Basketball_Reference_Structure_Guide.md': 'technical',
            'DATASET_STRUCTURE_DOCUMENTATION.md': 'technical',
            'NBA_TRAIN_DATA_STRUCTURE.md': 'technical',
            'NBA_API_Data_Fields_Complete.md': 'technical',
            'Data_Fields_Quick_Reference.md': 'technical',
            'Data_Structure_Example.md': 'technical',
            'SPLITTING_METHODOLOGY_DOCUMENTATION.md': 'technical',
            'SPLITTING_METHODOLOGY.md': 'technical',
            'README_DATA_PIPELINE.md': 'technical',
        }
        
        # Research documentation
        research_docs = {
            'How_NBA_Analytics_Work.md': 'research',
            'nba_statistics_explained.md': 'research',
            'four_factors_deep_dive.md': 'research',
            'basketball_reference_overview.md': 'research',
            'Odds_to_Probability_Guide.md': 'research',
            'Odds_Conversion_Practice.md': 'research',
            'Forecasting_Study_Guide.md': 'research',
            'FPP3_Chapters_1-2_Notes.md': 'research',
            'ML_Fundamentals_Notes.md': 'research',
            'Model_Evaluation_Metrics.md': 'research',
            'Metrics_Cheat_Sheet.md': 'research',
            'Log_Loss_Deep_Dive.md': 'research',
            'Calibration_Curves_Complete_Guide.md': 'research',
            'STATISTICS_QUICK_REFERENCE.md': 'research',
            'reddit_community_insights.md': 'research',
            'Market_Reasearch_-_Sports_Analytics.docx': 'research',
        }
        
        # Planning documentation
        planning_docs = {
            'project_roadmap.md': 'planning',
            'pre_launch_schedule.md': 'planning',
            'UPDATED_SCHEDULE_Week2-6.md': 'planning',
            'task_tracker.md': 'planning',
            'decision_log.md': 'planning',
            'Daily_Notes_Friday_Nov_21.md': 'planning',
            'week1_accomplishments_review.md': 'planning',
            'NBA_Decision_Summary.md': 'planning',
            'NBA_vs_NFL_Data_Comparison.md': 'planning',
            'THREE_APPROACHES_COMPARISON.md': 'planning',
            'MERGE_SUMMARY.md': 'planning',
        }
        
        # Move files
        all_docs = {**technical_docs, **research_docs, **planning_docs}
        
        for filename, category in all_docs.items():
            source = self.root / filename
            if source.exists():
                dest = self.root / 'docs' / category / filename
                shutil.move(str(source), str(dest))
                print(f"✓ Moved: {filename} → docs/{category}/")
        
        # Keep some files in root
        root_docs = [
            'INDEX.md',
            'homepage_copy.md',
            'about_page.md',
            'Website_style_idea',
            'INSTALLATION_CHECKLIST.md',
            'GIT_GITHUB_SETUP_GUIDE.md',
        ]
        
        print("\n✓ Keeping in root:")
        for doc in root_docs:
            if (self.root / doc).exists():
                print(f"  - {doc}")
    
    def organize_data_files(self):
        """Move data files to data/ directory."""
        print("\n" + "="*80)
        print("ORGANIZING DATA FILES")
        print("="*80 + "\n")
        
        # Move training data to processed
        data_files = {
            'nba_training_data.csv': 'processed',
            'nba_train_data.csv': 'processed',
        }
        
        for filename, category in data_files.items():
            source = self.root / filename
            if source.exists():
                dest = self.root / 'data' / category / filename
                shutil.move(str(source), str(dest))
                print(f"✓ Moved: {filename} → data/{category}/")
        
        print("\n⚠ Note: Add data/ directory to .gitignore (data files should not be committed)")
    
    def organize_scripts(self):
        """Move Python scripts to scripts/ directory."""
        print("\n" + "="*80)
        print("ORGANIZING SCRIPTS")
        print("="*80 + "\n")
        
        # Move python_refresher_code.py
        source = self.root / 'python_refresher_code.py'
        if source.exists():
            dest = self.root / 'scripts' / 'utils' / 'python_refresher_code.py'
            shutil.move(str(source), str(dest))
            print(f"✓ Moved: python_refresher_code.py → scripts/utils/")
        
        print("\n✓ Place new scripts in:")
        print("  - scripts/data_collection/ : API collection scripts")
        print("  - scripts/data_processing/ : Feature engineering, preprocessing")
        print("  - scripts/exploratory/ : EDA and analysis")
        print("  - scripts/modeling/ : Model training and evaluation")
        print("  - scripts/utils/ : Shared utilities")
    
    def create_gitignore(self):
        """Create comprehensive .gitignore file."""
        print("\n" + "="*80)
        print("CREATING .gitignore")
        print("="*80 + "\n")
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb_checkpoints/

# Data files (too large for Git)
data/
*.csv
*.parquet
*.pkl
*.h5
*.hdf5

# Model files
models/*.pkl
models/*.joblib
models/*.h5

# Output files
outputs/
*.png
*.jpg
*.pdf
results/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment variables
.env
.env.local

# Logs
*.log
logs/

# OS
Thumbs.db
.DS_Store

# Pytest
.pytest_cache/
.coverage
htmlcov/

# Keep certain files
!data/.gitkeep
!models/.gitkeep
!outputs/.gitkeep
!.gitkeep

# Documentation (keep these)
!*.md
!docs/**/*.md
"""
        
        gitignore_path = self.root / '.gitignore'
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        
        print("✓ Created .gitignore with comprehensive rules")
    
    def create_readme(self):
        """Create professional README.md."""
        print("\n" + "="*80)
        print("CREATING README.md")
        print("="*80 + "\n")
        
        readme_content = """# NBA Game Prediction Platform

A machine learning platform for predicting NBA game outcomes with transparent methodology and educational content. Built with XGBoost and modern NBA analytics principles.

## 🎯 Project Overview

This platform provides:
- **Accurate NBA game predictions** (target: 68-75% accuracy)
- **Transparent methodology** with explainable features
- **Educational content** on NBA analytics and machine learning
- **Model calibration** for probability-based predictions

**Launch Date:** January 1, 2026

## 📊 Key Features

- Uses Dean Oliver's Four Factors framework
- Net Rating Differential as primary predictor (r=0.324)
- XGBoost model with proper calibration
- No "black box" predictions - all methodology explained
- Focus on educational value alongside predictions

## 🏗️ Project Structure

```
nba-prediction-platform/
├── data/                    # Data files (not committed)
│   ├── raw/                # Raw API data
│   ├── processed/          # Cleaned datasets
│   └── external/           # External data sources
│
├── scripts/                 # Python scripts
│   ├── data_collection/    # API data collection
│   ├── data_processing/    # Feature engineering
│   ├── exploratory/        # EDA and analysis
│   ├── modeling/           # Model training
│   └── utils/              # Shared utilities
│
├── models/                  # Saved models
├── notebooks/               # Jupyter notebooks
├── docs/                    # Documentation
│   ├── technical/          # Technical docs
│   ├── research/           # Research notes
│   └── planning/           # Project planning
│
├── tests/                   # Unit tests
├── outputs/                 # Generated outputs
└── web/                     # Web application
```

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.12+
pip install -r requirements.txt
```

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/nba-prediction-platform.git
cd nba-prediction-platform

# Install dependencies
pip install -r requirements.txt

# Run feature engineering
python scripts/data_processing/feature_engineering.py

# Train model
python scripts/modeling/train_model.py
```

## 📈 Model Performance

**Target Metrics:**
- Accuracy: 68-75%
- Log Loss: < 0.60
- Calibration: Well-calibrated probabilities

**Current Results:**
- EDA completed with 3,924 games analyzed
- Net Rating Differential correlation: 0.324
- Feature engineering pipeline complete

## 🔬 Methodology

### Data Sources
- NBA API (`nba_api` library)
- Basketball-Reference.com (validation)
- 3+ seasons of historical data (2022-present)

### Key Features
1. **Net Rating Differential** (r=0.324)
2. **Win Percentage Differential** (r=0.286)
3. **Four Factors:**
   - Effective FG% (40% weight)
   - Turnover % (25% weight)
   - Offensive Rebound % (20% weight)
   - Free Throw Rate (15% weight)

### Model Architecture
- Primary: XGBoost Classifier
- Calibration: Platt Scaling / Isotonic Regression
- Validation: Chronological train/val/test split (70/15/15)

## 📚 Documentation

- **Technical Docs:** See `docs/technical/`
- **Research Notes:** See `docs/research/`
- **Planning:** See `docs/planning/`

## 🗓️ Development Timeline

- **Week 1 (✅ Complete):** Data infrastructure & EDA
- **Week 2:** Model training & optimization
- **Week 3:** Model refinement & calibration
- **Week 4:** Web platform development
- **Week 5:** Content creation & testing
- **Week 6:** Final polish & deployment

**Launch:** January 1, 2026

## 🤝 Contributing

This is currently a solo project, but feedback and suggestions are welcome!

## 📄 License

MIT License (or your choice)

## 👤 Author

Oleksandr - Building transparent, educational NBA analytics

## 🙏 Acknowledgments

- Dean Oliver's "Basketball on Paper"
- nba_api library maintainers
- Basketball-Reference.com
- NBA analytics community

---

**Note:** This platform is for educational and entertainment purposes. Always gamble responsibly.
"""
        
        readme_path = self.root / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print("✓ Created professional README.md")
    
    def create_requirements_txt(self):
        """Create requirements.txt with all dependencies."""
        print("\n" + "="*80)
        print("CREATING requirements.txt")
        print("="*80 + "\n")
        
        requirements = """# Core Data Science
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0

# Machine Learning
scikit-learn>=1.3.0
xgboost>=2.0.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# NBA Data
nba-api>=1.1.0

# Jupyter (for notebooks)
jupyter>=1.0.0
ipykernel>=6.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Utilities
python-dateutil>=2.8.0
pytz>=2023.3

# Web Framework (for future)
# fastapi>=0.100.0
# uvicorn>=0.23.0
"""
        
        req_path = self.root / 'requirements.txt'
        with open(req_path, 'w') as f:
            f.write(requirements)
        
        print("✓ Created requirements.txt")
    
    def run_organization(self):
        """Execute full project organization."""
        print("\n" + "="*80)
        print("NBA PREDICTION PLATFORM - PROJECT ORGANIZATION")
        print("="*80)
        print(f"\nProject root: {self.root}\n")
        
        # Create directory structure
        self.create_directory_structure()
        
        # Organize files
        self.organize_documentation_files()
        self.organize_data_files()
        self.organize_scripts()
        
        # Create project files
        self.create_gitignore()
        self.create_readme()
        self.create_requirements_txt()
        
        print("\n" + "="*80)
        print("PROJECT ORGANIZATION COMPLETE")
        print("="*80)
        print("\n✅ Your project is now organized and ready for GitHub!")
        print("\nNext steps:")
        print("1. Review the new structure")
        print("2. Initialize git: git init")
        print("3. Add files: git add .")
        print("4. Commit: git commit -m 'Initial commit: Organized project structure'")
        print("5. Create GitHub repo and push")
        print("\n⚠ Remember: The data/ directory is in .gitignore (files too large)")
        print("\n")


def main():
    """Main execution."""
    organizer = ProjectOrganizer()
    organizer.run_organization()


if __name__ == "__main__":
    main()