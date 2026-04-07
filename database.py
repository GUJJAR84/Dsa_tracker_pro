"""
database.py — dual database backend for DSA Tracker Pro.
Uses SQLite by default and PostgreSQL when DATABASE_URL is set.
"""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load local .env for development convenience.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
IS_POSTGRES = DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "tracker.db").strip() or "tracker.db"
DB_FILE = None if IS_POSTGRES else (Path(__file__).parent / SQLITE_DB_PATH)


def _sql(query: str) -> str:
    """Convert SQLite placeholders to PostgreSQL placeholders when needed."""
    if IS_POSTGRES:
        return query.replace("?", "%s")
    return query


def _row_to_dict(row):
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


def _last_insert_id(cur):
    if IS_POSTGRES:
        row = cur.fetchone()
        if isinstance(row, dict):
            return row.get("id")
        return row[0] if row else None
    return cur.lastrowid


# ─── Connection Helper ──────────────────────────────────────
@contextmanager
def get_conn():
    if IS_POSTGRES:
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(str(DB_FILE))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# ─── Schema ─────────────────────────────────────────────────
def init_db():
    if IS_POSTGRES:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                start_date TEXT,
                linkedin_posts INTEGER DEFAULT 0,
                github_commits INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                last_active TEXT,
                daily_target INTEGER DEFAULT 3
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS problems (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                platform TEXT DEFAULT 'LeetCode',
                problem_url TEXT DEFAULT '',
                difficulty TEXT DEFAULT 'Easy',
                pattern TEXT DEFAULT '',
                language TEXT DEFAULT 'Java',
                approach TEXT DEFAULT '',
                code TEXT DEFAULT '',
                time_complexity TEXT DEFAULT '',
                space_complexity TEXT DEFAULT '',
                time_taken INTEGER DEFAULT 0,
                independent INTEGER DEFAULT 0,
                confidence INTEGER DEFAULT 3,
                tags TEXT DEFAULT '[]',
                key_learnings TEXT DEFAULT '',
                mistakes TEXT DEFAULT '',
                date TEXT NOT NULL,
                revision_count INTEGER DEFAULT 0,
                last_revised TEXT,
                companies TEXT DEFAULT '[]'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                studied INTEGER DEFAULT 0,
                built INTEGER DEFAULT 0,
                posted INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                resources TEXT DEFAULT ''
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                description TEXT DEFAULT '',
                tech_stack TEXT DEFAULT '',
                github_url TEXT DEFAULT '',
                demo_url TEXT DEFAULT '',
                week1 INTEGER DEFAULT 0,
                week2 INTEGER DEFAULT 0,
                week3 INTEGER DEFAULT 0,
                week4 INTEGER DEFAULT 0,
                deployed INTEGER DEFAULT 0,
                week1_tasks TEXT DEFAULT '',
                week2_tasks TEXT DEFAULT '',
                week3_tasks TEXT DEFAULT '',
                week4_tasks TEXT DEFAULT ''
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS journal (
                id SERIAL PRIMARY KEY,
                date TEXT NOT NULL UNIQUE,
                content TEXT DEFAULT ''
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS contests (
                id SERIAL PRIMARY KEY,
                platform TEXT DEFAULT 'LeetCode',
                name TEXT DEFAULT '',
                date TEXT NOT NULL,
                rating INTEGER DEFAULT 0,
                rank INTEGER DEFAULT 0,
                problems_solved INTEGER DEFAULT 0,
                total_problems INTEGER DEFAULT 0,
                notes TEXT DEFAULT ''
            )
            """,
            "INSERT INTO settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING",
        ]
        with get_conn() as conn:
            for stmt in statements:
                conn.execute(stmt)

            cols = conn.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'problems'
                """
            ).fetchall()
            col_names = {r["column_name"] for r in cols}
            if "companies" not in col_names:
                conn.execute("ALTER TABLE problems ADD COLUMN companies TEXT DEFAULT '[]'")
    else:
        with get_conn() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS settings (
                id          INTEGER PRIMARY KEY CHECK (id = 1),
                start_date  TEXT,
                linkedin_posts INTEGER DEFAULT 0,
                github_commits INTEGER DEFAULT 0,
                streak      INTEGER DEFAULT 0,
                last_active TEXT,
                daily_target INTEGER DEFAULT 3
            );

            CREATE TABLE IF NOT EXISTS problems (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                platform        TEXT DEFAULT 'LeetCode',
                problem_url     TEXT DEFAULT '',
                difficulty      TEXT DEFAULT 'Easy',
                pattern         TEXT DEFAULT '',
                language        TEXT DEFAULT 'Java',
                approach        TEXT DEFAULT '',
                code            TEXT DEFAULT '',
                time_complexity TEXT DEFAULT '',
                space_complexity TEXT DEFAULT '',
                time_taken      INTEGER DEFAULT 0,
                independent     INTEGER DEFAULT 0,
                confidence      INTEGER DEFAULT 3,
                tags            TEXT DEFAULT '[]',
                key_learnings   TEXT DEFAULT '',
                mistakes        TEXT DEFAULT '',
                date            TEXT NOT NULL,
                revision_count  INTEGER DEFAULT 0,
                last_revised    TEXT,
                companies       TEXT DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS topics (
                id        TEXT PRIMARY KEY,
                studied   INTEGER DEFAULT 0,
                built     INTEGER DEFAULT 0,
                posted    INTEGER DEFAULT 0,
                notes     TEXT DEFAULT '',
                resources TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS projects (
                id          TEXT PRIMARY KEY,
                description TEXT DEFAULT '',
                tech_stack  TEXT DEFAULT '',
                github_url  TEXT DEFAULT '',
                demo_url    TEXT DEFAULT '',
                week1       INTEGER DEFAULT 0,
                week2       INTEGER DEFAULT 0,
                week3       INTEGER DEFAULT 0,
                week4       INTEGER DEFAULT 0,
                deployed    INTEGER DEFAULT 0,
                week1_tasks TEXT DEFAULT '',
                week2_tasks TEXT DEFAULT '',
                week3_tasks TEXT DEFAULT '',
                week4_tasks TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS journal (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                date    TEXT NOT NULL UNIQUE,
                content TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS contests (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                platform  TEXT DEFAULT 'LeetCode',
                name      TEXT DEFAULT '',
                date      TEXT NOT NULL,
                rating    INTEGER DEFAULT 0,
                rank      INTEGER DEFAULT 0,
                problems_solved INTEGER DEFAULT 0,
                total_problems  INTEGER DEFAULT 0,
                notes     TEXT DEFAULT ''
            );

            INSERT OR IGNORE INTO settings (id) VALUES (1);
            """)

        # Auto-migrate: add companies column if missing
        with get_conn() as conn:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(problems)").fetchall()]
            if 'companies' not in cols:
                conn.execute("ALTER TABLE problems ADD COLUMN companies TEXT DEFAULT '[]'")


# ═══════════════════════════════════════════════════════════
# ─── SETTINGS ─────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════
def get_settings():
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
        if row is None:
            conn.execute("INSERT INTO settings (id) VALUES (1)")
            row = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
        return _row_to_dict(row)


def update_settings(**kwargs):
    valid = {'start_date','linkedin_posts','github_commits','streak','last_active','daily_target'}
    fields = {k: v for k, v in kwargs.items() if k in valid}
    if not fields:
        return
    set_clause = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values())
    with get_conn() as conn:
        conn.execute(_sql(f"UPDATE settings SET {set_clause} WHERE id=1"), values)


# ═══════════════════════════════════════════════════════════
# ─── PROBLEMS ─────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════
def _row_to_problem(row):
    """Convert a DB row to a dict matching the old JSON format."""
    d = dict(row)
    d['independent'] = bool(d['independent'])
    try:
        d['tags'] = json.loads(d['tags']) if d['tags'] else []
    except (json.JSONDecodeError, TypeError):
        d['tags'] = []
    try:
        d['companies'] = json.loads(d.get('companies', '[]')) if d.get('companies') else []
    except (json.JSONDecodeError, TypeError):
        d['companies'] = []
    return d


def get_problems():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM problems ORDER BY id").fetchall()
    return [_row_to_problem(r) for r in rows]


def get_problem_count():
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM problems").fetchone()
        row_d = _row_to_dict(row)
        return row_d["cnt"]


def add_problem(p: dict) -> int:
    tags_json = json.dumps(p.get('tags', []))
    companies_json = json.dumps(p.get('companies', []))
    with get_conn() as conn:
        returning = " RETURNING id" if IS_POSTGRES else ""
        cur = conn.execute(_sql(f"""
            INSERT INTO problems (name, platform, problem_url, difficulty, pattern, language,
                approach, code, time_complexity, space_complexity, time_taken,
                independent, confidence, tags, key_learnings, mistakes, date,
                revision_count, last_revised, companies)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """ + returning), (
            p.get('name',''), p.get('platform','LeetCode'), p.get('problem_url',''),
            p.get('difficulty','Easy'), p.get('pattern',''), p.get('language','Java'),
            p.get('approach',''), p.get('code',''),
            p.get('time_complexity',''), p.get('space_complexity',''),
            p.get('time_taken',0), int(p.get('independent', False)),
            p.get('confidence',3), tags_json,
            p.get('key_learnings',''), p.get('mistakes',''),
            p.get('date',''), p.get('revision_count',0), p.get('last_revised'),
            companies_json
        ))
        return _last_insert_id(cur)


def update_problem(problem_id: int, **kwargs):
    valid = {
        'name','platform','problem_url','difficulty','pattern','language',
        'approach','code','time_complexity','space_complexity','time_taken',
        'independent','confidence','tags','key_learnings','mistakes',
        'date','revision_count','last_revised','companies'
    }
    fields = {}
    for k, v in kwargs.items():
        if k not in valid:
            continue
        if k in ('tags', 'companies'):
            fields[k] = json.dumps(v) if isinstance(v, list) else v
        elif k == 'independent':
            fields[k] = int(v)
        else:
            fields[k] = v
    if not fields:
        return
    set_clause = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [problem_id]
    with get_conn() as conn:
        conn.execute(_sql(f"UPDATE problems SET {set_clause} WHERE id=?"), values)


def delete_problem(problem_id: int):
    with get_conn() as conn:
        conn.execute(_sql("DELETE FROM problems WHERE id=?"), (problem_id,))


# ═══════════════════════════════════════════════════════════
# ─── TOPICS ───────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════
def get_topics() -> dict:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM topics ORDER BY id").fetchall()
    result = {}
    for r in rows:
        d = dict(r)
        tid = d.pop('id')
        d['studied'] = bool(d['studied'])
        d['built'] = bool(d['built'])
        d['posted'] = bool(d['posted'])
        result[tid] = d
    return result


def upsert_topic(tid: str, **kwargs):
    valid = {'studied','built','posted','notes','resources'}
    fields = {k: v for k, v in kwargs.items() if k in valid}
    for k in ('studied','built','posted'):
        if k in fields:
            fields[k] = int(fields[k])
    with get_conn() as conn:
        existing = conn.execute(_sql("SELECT id FROM topics WHERE id=?"), (tid,)).fetchone()
        if existing:
            if fields:
                set_clause = ", ".join(f"{k}=?" for k in fields)
                values = list(fields.values()) + [tid]
                conn.execute(_sql(f"UPDATE topics SET {set_clause} WHERE id=?"), values)
        else:
            cols = ['id'] + list(fields.keys())
            placeholders = ','.join(['?'] * len(cols))
            values = [tid] + list(fields.values())
            conn.execute(_sql(f"INSERT INTO topics ({','.join(cols)}) VALUES ({placeholders})"), values)


def add_topic(tid: str, data: dict = None):
    data = data or {}
    upsert_topic(tid,
        studied=data.get('studied', False),
        built=data.get('built', False),
        posted=data.get('posted', False),
        notes=data.get('notes', ''),
        resources=data.get('resources', '')
    )


# ═══════════════════════════════════════════════════════════
# ─── PROJECTS ─────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════
def get_projects() -> dict:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY id").fetchall()
    result = {}
    for r in rows:
        d = dict(r)
        pid = d.pop('id')
        for k in ('week1','week2','week3','week4','deployed'):
            d[k] = bool(d[k])
        result[pid] = d
    return result


def upsert_project(pid: str, **kwargs):
    valid = {
        'description','tech_stack','github_url','demo_url',
        'week1','week2','week3','week4','deployed',
        'week1_tasks','week2_tasks','week3_tasks','week4_tasks'
    }
    fields = {k: v for k, v in kwargs.items() if k in valid}
    for k in ('week1','week2','week3','week4','deployed'):
        if k in fields:
            fields[k] = int(fields[k])
    with get_conn() as conn:
        existing = conn.execute(_sql("SELECT id FROM projects WHERE id=?"), (pid,)).fetchone()
        if existing:
            if fields:
                set_clause = ", ".join(f"{k}=?" for k in fields)
                values = list(fields.values()) + [pid]
                conn.execute(_sql(f"UPDATE projects SET {set_clause} WHERE id=?"), values)
        else:
            cols = ['id'] + list(fields.keys())
            placeholders = ','.join(['?'] * len(cols))
            values = [pid] + list(fields.values())
            conn.execute(_sql(f"INSERT INTO projects ({','.join(cols)}) VALUES ({placeholders})"), values)


def add_project(pid: str, data: dict = None):
    data = data or {}
    upsert_project(pid,
        description=data.get('description', ''),
        tech_stack=data.get('tech_stack', ''),
        github_url=data.get('github_url', ''),
        demo_url=data.get('demo_url', ''),
        week1=data.get('week1', False),
        week2=data.get('week2', False),
        week3=data.get('week3', False),
        week4=data.get('week4', False),
        deployed=data.get('deployed', False),
        week1_tasks=data.get('week1_tasks', ''),
        week2_tasks=data.get('week2_tasks', ''),
        week3_tasks=data.get('week3_tasks', ''),
        week4_tasks=data.get('week4_tasks', ''),
    )


# ═══════════════════════════════════════════════════════════
# ─── MIGRATION FROM JSON ──────────────────────────────────
# ═══════════════════════════════════════════════════════════
def migrate_from_json(json_path: str):
    """One-time import: reads progress_data.json → inserts into SQLite."""
    p = Path(json_path)
    if not p.exists():
        print(f"No JSON file found at {p}")
        return False

    with open(p, 'r') as f:
        jdata = json.load(f)

    init_db()

    # Settings
    update_settings(
        start_date=jdata.get('start_date'),
        linkedin_posts=jdata.get('linkedin_posts', 0),
        github_commits=jdata.get('github_commits', 0),
        streak=jdata.get('streak', 0),
        last_active=jdata.get('last_active'),
        daily_target=jdata.get('daily_target', 3),
    )

    # Problems
    for prob in jdata.get('dsa', {}).get('problems', []):
        add_problem(prob)

    # Topics
    for tid, tdata in jdata.get('short_goals', {}).get('topics', {}).items():
        add_topic(tid, tdata)

    # Projects
    for pid, pdata in jdata.get('long_goals', {}).items():
        add_project(pid, pdata)

    # Backup the JSON file
    backup = p.with_suffix('.json.bak')
    p.rename(backup)
    print(f"✅ Migrated! JSON backed up to {backup}")
    print(f"   Problems: {get_problem_count()}")
    print(f"   Topics:   {len(get_topics())}")
    print(f"   Projects: {len(get_projects())}")
    return True


# ═══════════════════════════════════════════════════════════
# ─── JOURNAL ──────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════
def get_journal_entries():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM journal ORDER BY date DESC").fetchall()
    return [dict(r) for r in rows]


def get_journal_entry(date_str: str):
    with get_conn() as conn:
        row = conn.execute(_sql("SELECT * FROM journal WHERE date=?"), (date_str,)).fetchone()
    return _row_to_dict(row) if row else None


def upsert_journal(date_str: str, content: str):
    with get_conn() as conn:
        existing = conn.execute(_sql("SELECT id FROM journal WHERE date=?"), (date_str,)).fetchone()
        if existing:
            conn.execute(_sql("UPDATE journal SET content=? WHERE date=?"), (content, date_str))
        else:
            conn.execute(_sql("INSERT INTO journal (date, content) VALUES (?,?)"), (date_str, content))


# ═══════════════════════════════════════════════════════════
# ─── CONTESTS ─────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════
def get_contests():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM contests ORDER BY date DESC").fetchall()
    return [dict(r) for r in rows]


def add_contest(c: dict) -> int:
    with get_conn() as conn:
        returning = " RETURNING id" if IS_POSTGRES else ""
        cur = conn.execute(_sql(f"""
            INSERT INTO contests (platform, name, date, rating, rank, problems_solved, total_problems, notes)
            VALUES (?,?,?,?,?,?,?,?)
        """ + returning), (
            c.get('platform','LeetCode'), c.get('name',''), c.get('date',''),
            c.get('rating',0), c.get('rank',0),
            c.get('problems_solved',0), c.get('total_problems',0),
            c.get('notes','')
        ))
        return _last_insert_id(cur)


def delete_contest(contest_id: int):
    with get_conn() as conn:
        conn.execute(_sql("DELETE FROM contests WHERE id=?"), (contest_id,))


# Initialize on import
init_db()
