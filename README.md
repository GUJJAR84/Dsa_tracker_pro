# DSA Tracker Pro

DSA Tracker Pro is a Streamlit app for structured interview prep. It helps you track solved problems, revision cycles, company tags, learning topics, projects, contests, and progress analytics in one place.

## Features

- Dashboard with streaks, milestones, daily goals, weak pattern alerts, and weekly summary
- Problem logger with approach, code, complexity, confidence, tags, and company mapping
- NeetCode 150 roadmap with category progress and quick links
- Revision tracker, search/filter, daily journal, and mock interview timer
- Learning and long-project tracking with milestone checklists
- Analytics: difficulty, pattern, confidence, and activity trends
- Backup/export tools (Markdown, CSV, and SQLite backup in SQLite mode)

## Tech Stack

- Python + Streamlit
- Plotly for charts
- SQLite (default local mode)
- PostgreSQL (production mode via `DATABASE_URL`)

## Project Structure

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit app |
| `database.py` | Data layer (SQLite/PostgreSQL auto-switch) |
| `migrate_json.py` | Legacy JSON -> DB migration |
| `migrate_to_postgres.py` | SQLite -> PostgreSQL migration |
| `.streamlit/config.toml` | Streamlit runtime settings |
| `Procfile` | Start command for hosted platforms |
| `runtime.txt` | Python runtime pin |

## Local Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create local env file from template:

```powershell
Copy-Item .env.example .env
```

3. Run app:

```bash
python -m streamlit run app.py
```

## Database Modes

The app supports two modes automatically:

- SQLite mode: used when `DATABASE_URL` is empty
- PostgreSQL mode: used when `DATABASE_URL` starts with `postgres://` or `postgresql://`

If PostgreSQL is enabled, data is read/written directly to Neon (or any PostgreSQL provider).

## Migrate Existing Data to PostgreSQL

1. Create a PostgreSQL database (Neon recommended).
2. Put the connection string in `.env`:

```env
DATABASE_URL=REPLACE_WITH_YOUR_DATABASE_URL
```

3. Run migration:

```bash
python migrate_to_postgres.py
```

Notes:

- Existing `tracker.db` is not deleted.
- Migration is upsert-based, so re-running is safe.
- After migration, start app normally and it will use PostgreSQL.

## Deploy

### Streamlit Community Cloud (Recommended)

1. Push repository to GitHub.
2. Open Streamlit Cloud and create a new app.
3. Set main file path to `app.py`.
4. Add secret:

```toml
DATABASE_URL="REPLACE_WITH_YOUR_DATABASE_URL"
```

5. Deploy.

### Render (Alternative)

1. Create a Web Service from this repo.
2. Build command:

```bash
pip install -r requirements.txt
```

3. Start command:

```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true
```

4. Add `DATABASE_URL` environment variable.

## Secret Hygiene

- `.env` is git-ignored and must never be committed.
- Keep `.env.example` with placeholders only.
- Rotate DB credentials immediately if exposed.
- Pre-commit secret scanning is enabled with `.pre-commit-config.yaml`.

Setup hooks once:

```bash
pip install pre-commit detect-secrets
pre-commit install
pre-commit run --all-files
```
