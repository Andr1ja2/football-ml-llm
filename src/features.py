from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

from database import get_connection
from team_strength import compute_team_strength

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_base_df() -> pd.DataFrame:
    conn = get_connection()

    # Join matches with 1X2 odds (Bet365 only, you can extend later)
    query = """
    SELECT
        m.id AS match_id,
        m.date,
        m.home_team,
        m.away_team,
        m.home_goals,
        m.away_goals,
        m.full_time_result,
        MAX(CASE WHEN o.market = '1X2' AND o.outcome = 'home' THEN o.odds END) AS home_odds,
        MAX(CASE WHEN o.market = '1X2' AND o.outcome = 'draw' THEN o.odds END) AS draw_odds,
        MAX(CASE WHEN o.market = '1X2' AND o.outcome = 'away' THEN o.odds END) AS away_odds
    FROM matches m
    LEFT JOIN odds o ON o.match_id = m.id
    GROUP BY m.id
    ORDER BY m.date
    """
    df = pd.read_sql_query(query, conn, parse_dates=["date"])
    conn.close()

    # Drop rows without odds or result
    df = df.dropna(subset=["home_odds", "draw_odds", "away_odds", "full_time_result"])

    return df


def add_implied_probabilities(df: pd.DataFrame) -> pd.DataFrame:
    # Convert decimal odds to raw probabilities
    for col in ["home_odds", "draw_odds", "away_odds"]:
        df[f"{col}_rawp"] = 1.0 / df[col]

    # Bookmaker margin
    df["prob_sum"] = df["home_odds_rawp"] + df["draw_odds_rawp"] + df["away_odds_rawp"]

    # Normalize to remove margin
    df["home_prob"] = df["home_odds_rawp"] / df["prob_sum"]
    df["draw_prob"] = df["draw_odds_rawp"] / df["prob_sum"]
    df["away_prob"] = df["away_odds_rawp"] / df["prob_sum"]

    df = df.drop(columns=["prob_sum"])
    return df


def add_team_form_features(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    For each match, compute basic stats for each team based on past matches:
    - matches played
    - avg goals for / against
    - winrate
    """

    df = df.sort_values("date").reset_index(drop=True)

    # Initialize feature containers
    home_matches_played = []
    home_avg_gf = []
    home_avg_ga = []
    home_winrate = []

    away_matches_played = []
    away_avg_gf = []
    away_avg_ga = []
    away_winrate = []

    # Stats per team
    # We keep a rolling list of last "window" results
    team_history = {}  # team -> list of dicts: {"gf":..., "ga":..., "result": 'H'/'D'/'A'}

    def compute_stats(history_list):
        if len(history_list) == 0:
            return 0, 0.0, 0.0, 0.0
        # Last N matches
        last = history_list[-window:]
        n = len(last)
        gf = sum(h["gf"] for h in last)
        ga = sum(h["ga"] for h in last)
        wins = sum(1 for h in last if h["result"] == "W")
        return n, gf / n, ga / n, wins / n

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        hg = row["home_goals"]
        ag = row["away_goals"]

        # Initialize if missing
        if home not in team_history:
            team_history[home] = []
        if away not in team_history:
            team_history[away] = []

        # Compute stats BEFORE this match is added
        h_n, h_gf, h_ga, h_win = compute_stats(team_history[home])
        a_n, a_gf, a_ga, a_win = compute_stats(team_history[away])

        home_matches_played.append(h_n)
        home_avg_gf.append(h_gf)
        home_avg_ga.append(h_ga)
        home_winrate.append(h_win)

        away_matches_played.append(a_n)
        away_avg_gf.append(a_gf)
        away_avg_ga.append(a_ga)
        away_winrate.append(a_win)

        # Determine outcomes from home/away perspective
        if pd.isna(hg) or pd.isna(ag):
            # Skip updating history if goals missing
            continue

        hg = int(hg)
        ag = int(ag)

        if hg > ag:
            home_res = "W"
            away_res = "L"
        elif hg < ag:
            home_res = "L"
            away_res = "W"
        else:
            home_res = "D"
            away_res = "D"

        # Update history AFTER computing features
        team_history[home].append({"gf": hg, "ga": ag, "result": home_res})
        team_history[away].append({"gf": ag, "ga": hg, "result": away_res})

    df["home_matches_played"] = home_matches_played
    df["home_avg_gf"] = home_avg_gf
    df["home_avg_ga"] = home_avg_ga
    df["home_winrate"] = home_winrate

    df["away_matches_played"] = away_matches_played
    df["away_avg_gf"] = away_avg_gf
    df["away_avg_ga"] = away_avg_ga
    df["away_winrate"] = away_winrate

    return df


def encode_label(df: pd.DataFrame) -> pd.DataFrame:
    # full_time_result is 'H', 'D', 'A'
    label_map = {"H": 0, "D": 1, "A": 2}
    df = df[df["full_time_result"].isin(label_map.keys())].copy()
    df["label_1x2"] = df["full_time_result"].map(label_map)
    return df


def build_1x2_dataset():
    df = load_base_df()
    df = add_implied_probabilities(df)
    df = add_team_form_features(df, window=5)
    df = compute_team_strength(df)
    df = encode_label(df)

    # Drop rows where there was not enough history (optional)
    df = df[df["home_matches_played"] >= 1]
    df = df[df["away_matches_played"] >= 1]

    # Select feature columns
    feature_cols = [
        "home_prob",
        "draw_prob",
        "away_prob",

        "home_matches_played",
        "home_avg_gf",
        "home_avg_ga",
        "home_winrate",

        "away_matches_played",
        "away_avg_gf",
        "away_avg_ga",
        "away_winrate",

        "home_attack_strength",
        "home_defense_strength",

        "away_attack_strength",
        "away_defense_strength",
    ]

    out_df = df[["match_id", "date", "home_team", "away_team"] + feature_cols + ["label_1x2"]].copy()

    out_path = OUTPUT_DIR / "train_1x2.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Saved 1X2 training dataset to {out_path}")
    print(f"Rows: {len(out_df)}")


if __name__ == "__main__":
    build_1x2_dataset()
