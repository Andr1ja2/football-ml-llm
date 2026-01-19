import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "db.sqlite"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Matches table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        league TEXT,
        home_team TEXT,
        away_team TEXT,
        home_goals INTEGER,
        away_goals INTEGER,
        full_time_result TEXT
    );
    """)

    # Odds table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS odds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        bookie TEXT,
	market TEXT, -- e.g. "1X2", "BTTS", "GG2+"
	outcome TEXT, -- e.g. "home", "draw", "away"
        odds REAL,
        FOREIGN KEY(match_id) REFERENCES matches(id)
    );
    """)

    conn.commit()
    conn.close()
