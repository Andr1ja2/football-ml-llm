# Shared rolling team statistics used by training and live prediction.

from __future__ import annotations

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
    return {
        "matches_played": 0,
        "avg_gf": 0.0,
        "avg_ga": 0.0,
        "winrate": 0.0,
        "ppg": 0.0,
        "goal_diff": 0.0,
        "clean_sheet_rate": 0.0,
        "failed_to_score_rate": 0.0,
    }


def compute_rolling_stats(
    history: list[MatchRecord],
    window: int = FORM_WINDOW,
    venue: Literal["home", "away"] | None = None,
) -> StatDict:
    """Compute rolling stats from prior matches, optionally filtered by venue."""
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

    avg_gf = gf_total / n
    avg_ga = ga_total / n

    return {
        "matches_played": n,
        "avg_gf": avg_gf,
        "avg_ga": avg_ga,
        "winrate": wins / n,
        "ppg": points / n,
        "goal_diff": avg_gf - avg_ga,
        "clean_sheet_rate": clean_sheets / n,
        "failed_to_score_rate": failed_to_score / n,
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
    }


def result_from_goals(gf: int, ga: int) -> str:
    if gf > ga:
        return "W"
    if gf < ga:
        return "L"
    return "D"
