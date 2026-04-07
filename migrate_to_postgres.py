"""
One-time migration script: SQLite tracker.db -> PostgreSQL.

Usage (PowerShell):
    $env:DATABASE_URL="REPLACE_WITH_YOUR_DATABASE_URL"
  python migrate_to_postgres.py
"""
import os
import sqlite3
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

import database as db

SQLITE_PATH = Path(__file__).parent / "tracker.db"

TABLES = [
    ("users", "id"),
    ("settings", "user_id"),
    ("problems", "id"),
    ("topics", "id"),
    ("projects", "id"),
    ("journal", "date"),
    ("contests", "id"),
]


def q_ident(name: str) -> str:
    return f'"{name}"'


def get_sqlite_columns(conn: sqlite3.Connection, table: str):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [r[1] for r in rows]


def copy_table(sqlite_conn: sqlite3.Connection, pg_conn: psycopg.Connection, table: str, conflict_col: str):
    original_cols = get_sqlite_columns(sqlite_conn, table)
    cols = list(original_cols)
    if not cols:
        return 0

    if table == "settings":
        cols = [c for c in cols if c != "id"]
        if "user_id" not in cols:
            cols = ["user_id"] + cols

    col_list = ", ".join(q_ident(c) for c in cols)
    placeholders = ", ".join(["%s"] * len(cols))
    updatable = [c for c in cols if c != conflict_col]
    update_set = ", ".join(f'{q_ident(c)} = EXCLUDED.{q_ident(c)}' for c in updatable)

    if update_set:
        insert_sql = (
            f"INSERT INTO {q_ident(table)} ({col_list}) VALUES ({placeholders}) "
            f"ON CONFLICT ({q_ident(conflict_col)}) DO UPDATE SET {update_set}"
        )
    else:
        insert_sql = (
            f"INSERT INTO {q_ident(table)} ({col_list}) VALUES ({placeholders}) "
            f"ON CONFLICT ({q_ident(conflict_col)}) DO NOTHING"
        )

    if table == "settings" and "user_id" not in original_cols:
        select_cols = [c for c in original_cols if c != "id"]
        rows = [(0,) + tuple(row) for row in sqlite_conn.execute(f"SELECT {', '.join(select_cols)} FROM {table}").fetchall()]
    else:
        rows = sqlite_conn.execute(f"SELECT {', '.join(cols)} FROM {table}").fetchall()
    for row in rows:
        pg_conn.execute(insert_sql, tuple(row))
    return len(rows)


def reset_sequences(pg_conn: psycopg.Connection):
    pg_conn.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1), true)")
    pg_conn.execute("SELECT setval(pg_get_serial_sequence('problems', 'id'), COALESCE((SELECT MAX(id) FROM problems), 1), true)")
    pg_conn.execute("SELECT setval(pg_get_serial_sequence('journal', 'id'), COALESCE((SELECT MAX(id) FROM journal), 1), true)")
    pg_conn.execute("SELECT setval(pg_get_serial_sequence('contests', 'id'), COALESCE((SELECT MAX(id) FROM contests), 1), true)")


def main():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("DATABASE_URL is not set. Please set it to your PostgreSQL connection string.")

    if not SQLITE_PATH.exists():
        raise SystemExit(f"SQLite file not found: {SQLITE_PATH}")

    # Ensure PostgreSQL schema exists before copy.
    db.init_db()

    sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
    pg_conn = psycopg.connect(database_url, row_factory=dict_row)

    try:
        total = 0
        for table, conflict_col in TABLES:
            copied = copy_table(sqlite_conn, pg_conn, table, conflict_col)
            total += copied
            print(f"{table}: {copied} rows copied/upserted")

        reset_sequences(pg_conn)
        pg_conn.commit()
        print(f"\nDone. Total rows processed: {total}")
        print("Your existing SQLite data is preserved. PostgreSQL now has a synced copy.")
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
