"""
migrate_json.py — One-time migration from progress_data.json to tracker.db
Run: python migrate_json.py
"""
from database import migrate_from_json

if __name__ == "__main__":
    migrate_from_json("progress_data.json")
