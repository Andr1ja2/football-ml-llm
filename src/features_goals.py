# build_goal_features: For each match, compute basic stats for each team based on past matches: 
# matches played, BTTS rate, avg goals scored. Also compute the target variables: BTTS (both teams to score) and OVER_2_5 (total goals >= 3).
from pathlib import Path
import pandas as pd

from database import get_connection

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW = 5

def load_matches():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT id, date, home_team, away_team,
               home_goals, away_goals
        FROM matches
        WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
        ORDER BY date
        """,
        conn,
        parse_dates=["date"]
    )
    conn.close()
    return df

def build_goal_features(df):
    team_hist = {}

    rows = []

    for _, r in df.iterrows():
        h, a = r.home_team, r.away_team

        for t in (h, a):
            if t not in team_hist:
                team_hist[t] = []

        def stats(team):
            hist = team_hist[team][-WINDOW:]
            if not hist:
                return 0, 0.0, 0.0
            btts_rate = sum(x["btts"] for x in hist) / len(hist)
            avg_goals = sum(x["goals"] for x in hist) / len(hist)
            return len(hist), btts_rate, avg_goals

        h_n, h_btts, h_avg_goals = stats(h)
        a_n, a_btts, a_avg_goals = stats(a)

        total_goals = r.home_goals + r.away_goals
        btts = int(r.home_goals > 0 and r.away_goals > 0)

        rows.append({
            "match_id": r.id,
            "date": r.date,
            "home_team": h,
            "away_team": a,
            "home_hist_n": h_n,
            "home_btts_rate": h_btts,
            "home_avg_goals": h_avg_goals,
            "away_hist_n": a_n,
            "away_btts_rate": a_btts,
            "away_avg_goals": a_avg_goals,
            "BTTS": btts,
            "OVER_2_5": int(total_goals >= 3)
        })

        team_hist[h].append({
            "btts": btts,
            "goals": total_goals
        })
        team_hist[a].append({
            "btts": btts,
            "goals": total_goals
        })

    out = pd.DataFrame(rows)
    out = out[(out.home_hist_n > 0) & (out.away_hist_n > 0)]

    return out

def main():
    df = load_matches()
    feats = build_goal_features(df)

    feats.to_csv(OUTPUT_DIR / "train_btts_ou.csv", index=False)
    print(f"Saved BTTS/OU dataset with {len(feats)} rows")

if __name__ == "__main__":
    main()
