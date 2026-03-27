# 🎯 12-Week Progress Tracker

A Streamlit app to track your DSA practice, ML learning, and project progress.

## Features

- **📊 Dashboard** — Overview of all progress with daily logging
- **💻 DSA Tracker** — Log problems with approach, solution code, complexity analysis, platform, confidence, and more
- **📖 Problem Solutions** — Browse and review all saved solutions with syntax-highlighted code
- **🗺️ NeetCode 150** — Visual roadmap showing your progress across all NeetCode 150 categories
- **🔄 Revision Tracker** — Spaced repetition system to revisit low-confidence problems
- **🔍 Search & Filter** — Find problems by name, platform, difficulty, or pattern
- **📚 Learning (Short Goals)** — 16 ML topics checklist
- **🏗️ Projects (Long Goals)** — 3 project milestones
- **📈 Analytics** — Difficulty distribution, platform stats, confidence charts, time analysis, weekly heatmap
- **📥 Export** — Download all solutions as a formatted Markdown file

## How to Run

```bash
pip install streamlit>=1.28.0
cd TRACKER_APP
streamlit run app.py
```

Opens at `http://localhost:8501`

## Data Storage

All progress is saved in `progress_data.json`. Existing data is auto-migrated when new fields are added.
