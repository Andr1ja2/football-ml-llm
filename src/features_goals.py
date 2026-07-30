# Build BTTS / Over-Under 2.5 training dataset.
#
# Reuses the same rolling-stats and team-strength primitives as the 1X2
# pipeline (team_stats.py + team_strength.py) so the BTTS/OU dataset and
# the 1X2 dataset share a single source of truth for per-team statistics.

from pathlib import Path

import pandas as pd

from database import get_connection
from feature_defs import FEATURE_COLS_BTTS_OU
from team_stats import (
    MatchRecord,
    compute_rolling_stats,
    result_from_goals,
    stats_to_feature_values,
)
from team_strength import compute_team_strength

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_matches() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT id AS match_id, date, league, home_team, away_team, home_goals, away_goals
        FROM matches
        WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
        ORDER BY date
        """,
        conn,
        parse_dates=["date"],
    )
    conn.close()
    return df


def add_goal_form_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-team rolling stats using only prior matches (no leakage)."""
    df = df.sort_values("date").reset_index(drop=True)

    team_history: dict[str, list[MatchRecord]] = {}
    feature_rows: list[dict[str, float | int]] = []

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]

        team_history.setdefault(home, [])
        team_history.setdefault(away, [])

        home_overall = compute_rolling_stats(team_history[home])
        away_overall = compute_rolling_stats(team_history[away])

        features: dict[str, float | int] = {}
        features.update(stats_to_feature_values(home_overall, "home"))
        features.update(stats_to_feature_values(away_overall, "away"))
        feature_rows.append(features)

        hg = int(row["home_goals"])
        ag = int(row["away_goals"])

        team_history[home].append(
            MatchRecord(gf=hg, ga=ag, result=result_from_goals(hg, ag), venue="home")
        )
        team_history[away].append(
            MatchRecord(gf=ag, ga=hg, result=result_from_goals(ag, hg), venue="away")
        )

    feature_df = pd.DataFrame(feature_rows)
    return pd.concat([df, feature_df], axis=1)


def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Derive BTTS (both teams scored) and Over/Under 2.5 labels."""
    df["BTTS"] = ((df["home_goals"] > 0) & (df["away_goals"] > 0)).astype(int)
    df["OVER_2_5"] = ((df["home_goals"] + df["away_goals"]) >= 3).astype(int)
    return df


def build_goal_dataset() -> pd.DataFrame:
    df = load_matches()
    df = add_goal_form_features(df)
    df = compute_team_strength(df)
    df = add_targets(df)

    # Require at least one prior match for both sides so stats are defined.
    df = df[df["home_matches_played"] >= 1]
    df = df[df["away_matches_played"] >= 1]

    out_df = df[
        ["match_id", "date", "home_team", "away_team"]
        + FEATURE_COLS_BTTS_OU
        + ["BTTS", "OVER_2_5"]
    ].copy()

    return out_df


def main() -> None:
    out_df = build_goal_dataset()

    out_path = OUTPUT_DIR / "train_btts_ou.csv"
    out_df.to_csv(out_path, index=False)

    print(f"Saved BTTS/OU training dataset to {out_path}")
    print(f"Rows: {len(out_df)}")
    print(f"Features: {len(FEATURE_COLS_BTTS_OU)}")


if __name__ == "__main__":
    main()
