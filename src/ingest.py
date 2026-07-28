# This script imports raw CSV data into the SQLite database. It assumes that the database schema has already been created.
# For every row it read: home team, away team, goals, result, odds and date. It then inserts the data into the matches and odds tables.
import csv
from pathlib import Path
from database import get_connection

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Mapping from FTR to H/D/A
RESULT_MAP = {
    "H": "H",
    "D": "D",
    "A": "A",
}

def ingest_csv(file_path: Path, league: str):
    conn = get_connection()
    cur = conn.cursor()

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            date = row.get("Date")
            home = row.get("HomeTeam")
            away = row.get("AwayTeam")
            home_goals = int(row.get("FTHG")) if row.get("FTHG") else None
            away_goals = int(row.get("FTAG")) if row.get("FTAG") else None
            ftr = RESULT_MAP.get(row.get("FTR"))

            # Insert match
            cur.execute("""
                INSERT INTO matches (date, league, home_team, away_team, home_goals, away_goals, full_time_result)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, league, home, away, home_goals, away_goals, ftr))

            match_id = cur.lastrowid

            # Insert odds (1X2 only for now)
            home_odds = row.get("B365H")
            draw_odds = row.get("B365D")
            away_odds = row.get("B365A")

            if home_odds and draw_odds and away_odds:
                cur.execute("""
                    INSERT INTO odds (match_id, bookie, market, outcome, odds)
                    VALUES (?, ?, ?, ?, ?)
                """, (match_id, "Bet365", "1X2", "home", float(home_odds)))

                cur.execute("""
                    INSERT INTO odds (match_id, bookie, market, outcome, odds)
                    VALUES (?, ?, ?, ?, ?)
                """, (match_id, "Bet365", "1X2", "draw", float(draw_odds)))

                cur.execute("""
                    INSERT INTO odds (match_id, bookie, market, outcome, odds)
                    VALUES (?, ?, ?, ?, ?)
                """, (match_id, "Bet365", "1X2", "away", float(away_odds)))

    conn.commit()
    conn.close()

    print(f"Ingested {file_path.name} for league {league}")


def ingest_all():
    for file in RAW_DATA_DIR.glob("*.csv"):
        league = "UNKNOWN"
        ingest_csv(file, league)


if __name__ == "__main__":
    ingest_all()
