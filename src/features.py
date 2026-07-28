# load_base_df: Load matches and odds from the database, join them, and return a DataFrame.
# add_implied_probabilities: Convert decimal odds to implied probabilities and normalize them.
# add_team_form_features: Rolling team stats from prior matches only (overall + venue splits).
# encode_label: Maps full_time_result to a numeric label: H -> 0, D -> 1, A -> 2.
# build_1x2_dataset: Main function that combines all steps to build the final dataset for 1X2 prediction.
from pathlib import Path

import numpy as np
import pandas as pd

from database import get_connection
from feature_defs import FEATURE_COLS_1X2, FORM_WINDOW
from team_stats import MatchRecord, compute_rolling_stats, result_from_goals, stats_to_feature_values
from team_strength import compute_team_strength

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_base_df() -> pd.DataFrame:
    conn = get_connection()

    query = """
    SELECT
        m.id AS match_id,
        m.date,
        m.league,
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

    df = df.dropna(subset=["home_odds", "draw_odds", "away_odds", "full_time_result"])
    return df


def add_implied_probabilities(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["home_odds", "draw_odds", "away_odds"]:
        df[f"{col}_rawp"] = 1.0 / df[col]

    df["prob_sum"] = df["home_odds_rawp"] + df["draw_odds_rawp"] + df["away_odds_rawp"]

    df["home_prob"] = df["home_odds_rawp"] / df["prob_sum"]
    df["draw_prob"] = df["draw_odds_rawp"] / df["prob_sum"]
    df["away_prob"] = df["away_odds_rawp"] / df["prob_sum"]

    df = df.drop(columns=["prob_sum"])
    return df


def add_team_form_features(df: pd.DataFrame, window: int = FORM_WINDOW) -> pd.DataFrame:
    """Compute rolling team stats from matches played before each row."""
    df = df.sort_values("date").reset_index(drop=True)

    team_history: dict[str, list[MatchRecord]] = {}
    feature_rows: list[dict[str, float | int]] = []

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]

        team_history.setdefault(home, [])
        team_history.setdefault(away, [])

        home_overall = compute_rolling_stats(team_history[home], window=window)
        home_venue = compute_rolling_stats(team_history[home], window=window, venue="home")
        away_overall = compute_rolling_stats(team_history[away], window=window)
        away_venue = compute_rolling_stats(team_history[away], window=window, venue="away")

        features: dict[str, float | int] = {}
        features.update(stats_to_feature_values(home_overall, "home"))
        features.update(stats_to_feature_values(home_venue, "home_home"))
        features.update(stats_to_feature_values(away_overall, "away"))
        features.update(stats_to_feature_values(away_venue, "away_away"))
        feature_rows.append(features)

        hg = row["home_goals"]
        ag = row["away_goals"]
        if pd.isna(hg) or pd.isna(ag):
            continue

        hg = int(hg)
        ag = int(ag)

        team_history[home].append(
            MatchRecord(gf=hg, ga=ag, result=result_from_goals(hg, ag), venue="home")
        )
        team_history[away].append(
            MatchRecord(gf=ag, ga=hg, result=result_from_goals(ag, hg), venue="away")
        )

    feature_df = pd.DataFrame(feature_rows)
    return pd.concat([df, feature_df], axis=1)


def encode_label(df: pd.DataFrame) -> pd.DataFrame:
    label_map = {"H": 0, "D": 1, "A": 2}
    df = df[df["full_time_result"].isin(label_map.keys())].copy()
    df["label_1x2"] = df["full_time_result"].map(label_map)
    return df


def build_1x2_dataset() -> None:
    df = load_base_df()
    df = add_implied_probabilities(df)
    df = add_team_form_features(df, window=FORM_WINDOW)
    df = compute_team_strength(df, window=FORM_WINDOW)
    df = encode_label(df)

    df = df[df["home_matches_played"] >= 1]
    df = df[df["away_matches_played"] >= 1]

    out_df = df[["match_id", "date", "home_team", "away_team"] + FEATURE_COLS_1X2 + ["label_1x2"]].copy()

    out_path = OUTPUT_DIR / "train_1x2.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Saved 1X2 training dataset to {out_path}")
    print(f"Rows: {len(out_df)}")
    print(f"Features: {len(FEATURE_COLS_1X2)}")


if __name__ == "__main__":
    build_1x2_dataset()
