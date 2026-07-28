# Rolling team statistics for live prediction with fuzzy name resolution.

from __future__ import annotations

from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz, process

from database import get_connection
from feature_defs import FORM_WINDOW
from team_stats import MatchRecord, compute_rolling_stats, result_from_goals, stats_to_feature_values
from team_strength import _team_strength

FUZZ_THRESHOLD = 90


def normalize_name(name: str) -> str:
    name = name.lower()
    for suffix in (" fc", " cf", " afc", " football club", " united"):
        name = name.replace(suffix, "")
    return name.replace(".", "").strip()


def load_match_history() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT date, league, home_team, away_team, home_goals, away_goals
        FROM matches
        WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
        """,
        conn,
    )
    conn.close()

    df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True, errors="raise")
    df = df.dropna(subset=["date"])
    return df.sort_values("date").reset_index(drop=True)


class TeamResolver:
    def __init__(self, df: pd.DataFrame):
        teams = set(df["home_team"].unique()) | set(df["away_team"].unique())
        self.original_teams = list(teams)
        self.normalized_map = {normalize_name(t): t for t in self.original_teams}
        self.cache: dict[str, str | None] = {}

    def resolve(self, name: str) -> str | None:
        if name in self.cache:
            return self.cache[name]

        norm = normalize_name(name)
        if norm in self.normalized_map:
            resolved = self.normalized_map[norm]
            self.cache[name] = resolved
            return resolved

        match = process.extractOne(norm, list(self.normalized_map.keys()), scorer=fuzz.ratio)
        if match and match[1] >= FUZZ_THRESHOLD:
            resolved = self.normalized_map[match[0]]
            self.cache[name] = resolved
            return resolved

        self.cache[name] = None
        return None


def _build_team_history(df: pd.DataFrame, resolved: str) -> list[MatchRecord]:
    history: list[MatchRecord] = []
    for _, row in df.iterrows():
        if row["home_team"] == resolved:
            gf, ga = int(row["home_goals"]), int(row["away_goals"])
            venue = "home"
        elif row["away_team"] == resolved:
            gf, ga = int(row["away_goals"]), int(row["home_goals"])
            venue = "away"
        else:
            continue

        history.append(
            MatchRecord(gf=gf, ga=ga, result=result_from_goals(gf, ga), venue=venue)
        )
    return history


def _compute_strength_for_team(
    df: pd.DataFrame,
    resolved: str,
    window: int = FORM_WINDOW,
) -> tuple[float, float]:
    """Compute league-relative strength using all prior matches in the history dataframe."""
    league_hist: dict[str, list[tuple[int, int]]] = defaultdict(list)
    team_hist: dict[str, list[dict[str, int]]] = defaultdict(list)

    attack, defense = 1.0, 1.0

    for _, row in df.iterrows():
        league = str(row.get("league", "UNKNOWN"))
        home = row["home_team"]
        away = row["away_team"]
        hg = int(row["home_goals"])
        ag = int(row["away_goals"])

        if home == resolved or away == resolved:
            attack, defense = _team_strength(
                resolved, league, team_hist, league_hist, window
            )

        league_hist[league].append((hg, ag))
        team_hist[home].append({"gf": hg, "ga": ag})
        team_hist[away].append({"gf": ag, "ga": hg})

    return attack, defense


def compute_team_stats(
    df: pd.DataFrame,
    resolver: TeamResolver,
    team_name: str,
    window: int = FORM_WINDOW,
) -> dict[str, float | int] | None:
    """
    Compute the same feature set used in training for a single team at prediction time.
    Returns a flat dict keyed by feature column names (home_* or away_* prefixes applied by caller).
    """
    resolved = resolver.resolve(team_name)
    if resolved is None:
        return None

    history = _build_team_history(df, resolved)
    if not history:
        return None

    overall = compute_rolling_stats(history, window=window)
    home_venue = compute_rolling_stats(history, window=window, venue="home")
    away_venue = compute_rolling_stats(history, window=window, venue="away")
    attack, defense = _compute_strength_for_team(df, resolved, window=window)

    stats = {
        **overall,
        "home_venue": home_venue,
        "away_venue": away_venue,
        "attack_strength": attack,
        "defense_strength": defense,
    }
    return stats


def build_live_feature_dict(
    home_stats: dict,
    away_stats: dict,
    book_probs: list[float],
) -> dict[str, float | int]:
    """Assemble a flat feature dict matching FEATURE_COLS_1X2 column names."""
    features: dict[str, float | int] = {
        "home_prob": book_probs[0],
        "draw_prob": book_probs[1],
        "away_prob": book_probs[2],
    }
    features.update(stats_to_feature_values(home_stats, "home"))
    features.update(stats_to_feature_values(home_stats["home_venue"], "home_home"))
    features.update(stats_to_feature_values(away_stats, "away"))
    features.update(stats_to_feature_values(away_stats["away_venue"], "away_away"))
    features["home_attack_strength"] = home_stats["attack_strength"]
    features["home_defense_strength"] = home_stats["defense_strength"]
    features["away_attack_strength"] = away_stats["attack_strength"]
    features["away_defense_strength"] = away_stats["defense_strength"]
    return features
