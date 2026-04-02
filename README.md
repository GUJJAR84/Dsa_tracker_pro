# 🚀 DSA Tracker Pro

A comprehensive DSA problem tracker built with **Streamlit** and **SQLite** — designed for serious interview preparation.

## ✨ Features

### Core Tracking
- **📊 Dashboard** — Progress metrics, streak tracker, milestone badges, weekly summary, weak pattern alerts
- **💻 DSA Tracker** — Log problems with approach, code, complexity, tags, and company tags
- **📖 Problem Solutions** — Searchable journal with inline edit, delete, pagination
- **🗺️ NeetCode 150** — Complete roadmap with per-category progress and one-click solve buttons

### Interview Prep
- **⏱️ Mock Interview** — Timed practice with random problem selection and countdown timer
- **🏢 Company Tags** — Tag problems by company (Google, Amazon, etc.) and filter by target company
- **🔄 Revision Tracker** — Spaced repetition system ranked by confidence and recency

### Learning & Projects
- **📚 Learning (Short)** — Track study topics with studied/built/posted checkboxes, notes, resources
- **🏗️ Projects (Long)** — Weekly milestones, deploy status, tech stack, GitHub/demo links
- **🏆 Contest Tracker** — Log contest ratings, rankings, and track progress over time

### Analytics & Insights
- **📈 Analytics** — Difficulty/pattern/platform/confidence charts, GitHub-style calendar heatmap
- **📋 Pattern Performance** — Per-pattern stats table (avg confidence, avg time, independence rate)

### Utilities
- **🔍 Search & Filter** — Filter by platform, difficulty, pattern, tag, company, confidence
- **📓 Daily Journal** — Quick daily reflections and learning notes
- **📤 Progress Card** — Generate a shareable stats card for LinkedIn
- **💾 Backup/Restore** — One-click database backup and restore
- **📥 Export** — Markdown and CSV export of all solutions
- **🌗 Light/Dark Mode** — Toggle between light and dark themes

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **Database:** SQLite (WAL mode, ACID-compliant)
- **Charts:** Plotly

## 🚀 Quick Start

```bash
pip install streamlit plotly
python -m streamlit run app.py
```

## 📁 Files

| File | Purpose |
|---|---|
| `app.py` | Main application (all pages) |
| `database.py` | SQLite schema + CRUD helpers |
| `migrate_json.py` | One-time JSON → SQLite migration |
| `tracker.db` | Your data (auto-created, gitignored) |
