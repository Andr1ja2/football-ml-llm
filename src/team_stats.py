# Shared rolling team statistics used by training and live prediction.
# Single source of truth for per-team rolling metrics (1X2 form, BTTS, OU 2.5).

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Literal

from feature_defs import FORM_WINDOW

POINTS = {"W": 3, "D": 1, "L": 0}

StatDict = dict[str, float | int]


@dataclass
class MatchRecord:
    gf: int
    ga: int
    result: str
    venue: Literal["home", "away"]


def empty_stats() -> StatDict:
    """Zero-valued stat dict returned when a team has no history yet."""
    return {
        "matches_played": 0,
        "avg_gf": 0.0,
        "avg_ga": 0.0,
        "winrate": 0.0,
        "ppg": 0.0,
        "goal_diff": 0.0,
        "clean_sheet_rate": 0.0,
        "failed_to_score_rate": 0.0,
        "btts_rate": 0.0,
        "avg_goals": 0.0,
        "avg_goals_for": 0.0,
        "avg_goals_against": 0.0,
        "goals_last5": 0,
        "scored_rate_last5": 0.0,
        "goals_conceded_last5": 0,
        "conceded_rate_last5": 0.0,
        "goal_std": 0.0,
    }


def compute_rolling_stats(
    history: list[MatchRecord],
    window: int = FORM_WINDOW,
    venue: Literal["home", "away"] | None = None,
) -> StatDict:
    """Compute rolling stats from prior matches, optionally filtered by venue.

    Returns the union of 1X2 form stats and goal-related stats so all training
    pipelines can derive their features from a single call.
    """
    if venue is not None:
        history = [m for m in history if m.venue == venue]

    if not history:
        return empty_stats()

    last = history[-window:]
    n = len(last)

    gf_total = sum(m.gf for m in last)
    ga_total = sum(m.ga for m in last)
    wins = sum(1 for m in last if m.result == "W")
    points = sum(POINTS[m.result] for m in last)
    clean_sheets = sum(1 for m in last if m.ga == 0)
    failed_to_score = sum(1 for m in last if m.gf == 0)
    btts_count = sum(1 for m in last if m.gf > 0 and m.ga > 0)
    scored_count = sum(1 for m in last if m.gf > 0)
    conceded_count = sum(1 for m in last if m.ga > 0)

    avg_gf = gf_total / n
    avg_ga = ga_total / n
    avg_goals_per_match = (gf_total + ga_total) / n

    # Standard deviation of total goals per match (OU 2.5 variance proxy).
    goal_std = (
        statistics.pstdev(m.gf + m.ga for m in last) if n > 1 else 0.0
    )

    return {
        "matches_played": n,
        "avg_gf": avg_gf,
        "avg_ga": avg_ga,
        "winrate": wins / n,
        "ppg": points / n,
        "goal_diff": avg_gf - avg_ga,
        "clean_sheet_rate": clean_sheets / n,
        "failed_to_score_rate": failed_to_score / n,
        "btts_rate": btts_count / n,
        "avg_goals": avg_goals_per_match,
        "avg_goals_for": avg_gf,
        "avg_goals_against": avg_ga,
        "goals_last5": int(gf_total),
        "scored_rate_last5": scored_count / n,
        "goals_conceded_last5": int(ga_total),
        "conceded_rate_last5": conceded_count / n,
        "goal_std": float(goal_std),
    }


def stats_to_feature_values(stats: StatDict, prefix: str) -> dict[str, float | int]:
    """Map stat dict keys to feature column names with a given prefix."""
    return {
        f"{prefix}_matches_played": stats["matches_played"],
        f"{prefix}_avg_gf": stats["avg_gf"],
        f"{prefix}_avg_ga": stats["avg_ga"],
        f"{prefix}_winrate": stats["winrate"],
        f"{prefix}_ppg": stats["ppg"],
        f"{prefix}_goal_diff": stats["goal_diff"],
        f"{prefix}_clean_sheet_rate": stats["clean_sheet_rate"],
        f"{prefix}_failed_to_score_rate": stats["failed_to_score_rate"],
        f"{prefix}_btts_rate": stats["btts_rate"],
        f"{prefix}_avg_goals": stats["avg_goals"],
        f"{prefix}_avg_goals_for": stats["avg_goals_for"],
        f"{prefix}_avg_goals_against": stats["avg_goals_against"],
        f"{prefix}_goals_last5": stats["goals_last5"],
        f"{prefix}_scored_rate_last5": stats["scored_rate_last5"],
        f"{prefix}_goals_conceded_last5": stats["goals_conceded_last5"],
        f"{prefix}_conceded_rate_last5": stats["conceded_rate_last5"],
        f"{prefix}_goal_std": stats["goal_std"],
    }


def result_from_goals(gf: int, ga: int) -> str:
    if gf > ga:
        return "W"
    if gf < ga:
        return "L"
    return "D"
