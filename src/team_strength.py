# League-relative attack and defense strength features.

from __future__ import annotations

from collections import defaultdict

import pandas as pd

from feature_defs import FORM_WINDOW

DEFAULT_STRENGTH = 1.0


def compute_team_strength(df: pd.DataFrame, window: int = FORM_WINDOW) -> pd.DataFrame:
    """
    Compute league-relative attack/defense strength using only prior matches.

    attack_strength = team_avg_goals_scored / league_avg_goals_scored
    defense_strength = league_avg_goals_conceded / team_avg_goals_conceded
    """
    df = df.sort_values("date").reset_index(drop=True)

    league_hist: dict[str, list[tuple[int, int]]] = defaultdict(list)
    team_hist: dict[str, list[dict[str, int]]] = defaultdict(list)

    home_attack: list[float] = []
    home_defense: list[float] = []
    away_attack: list[float] = []
    away_defense: list[float] = []

    for _, row in df.iterrows():
        league = str(row.get("league", "UNKNOWN"))
        home = row["home_team"]
        away = row["away_team"]

        h_att, h_def = _team_strength(home, league, team_hist, league_hist, window)
        a_att, a_def = _team_strength(away, league, team_hist, league_hist, window)

        home_attack.append(h_att)
        home_defense.append(h_def)
        away_attack.append(a_att)
        away_defense.append(a_def)

        hg = row["home_goals"]
        ag = row["away_goals"]
        if pd.isna(hg) or pd.isna(ag):
            continue

        hg = int(hg)
        ag = int(ag)

        league_hist[league].append((hg, ag))
        team_hist[home].append({"gf": hg, "ga": ag})
        team_hist[away].append({"gf": ag, "ga": hg})

    df["home_attack_strength"] = home_attack
    df["home_defense_strength"] = home_defense
    df["away_attack_strength"] = away_attack
    df["away_defense_strength"] = away_defense

    return df


def _team_strength(
    team: str,
    league: str,
    team_hist: dict[str, list[dict[str, int]]],
    league_hist: dict[str, list[tuple[int, int]]],
    window: int,
) -> tuple[float, float]:
    hist = team_hist[team][-window:]
    if not hist:
        return DEFAULT_STRENGTH, DEFAULT_STRENGTH

    team_avg_scored = sum(m["gf"] for m in hist) / len(hist)
    team_avg_conceded = sum(m["ga"] for m in hist) / len(hist)

    league_avg_scored, league_avg_conceded = _league_averages(league_hist.get(league, []))

    attack = team_avg_scored / league_avg_scored if league_avg_scored > 0 else DEFAULT_STRENGTH
    defense = (
        league_avg_conceded / team_avg_conceded
        if team_avg_conceded > 0
        else DEFAULT_STRENGTH
    )

    return attack, defense


def _league_averages(matches: list[tuple[int, int]]) -> tuple[float, float]:
    """Average goals scored/conceded per team per match in the league."""
    if not matches:
        return 1.0, 1.0

    total_goals = sum(hg + ag for hg, ag in matches)
    n_team_matches = len(matches) * 2
    avg = total_goals / n_team_matches
    return avg, avg
