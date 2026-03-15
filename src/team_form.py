from unicodedata import name

import pandas as pd
from database import get_connection
from rapidfuzz import process, fuzz

WINDOW = 5
FUZZ_THRESHOLD = 90  # safe threshold (team name matches 90%)

def normalize_name(name: str) -> str:
    name = name.lower()
    name = name.replace(".", "")
    name = name.replace(" fc", "")
    name = name.replace(" cf", "")
    name = name.replace(" afc", "")
    name = name.replace(" football club", "")
    name = name.replace(" united", "")
    name = name.strip()
    return name


def load_match_history():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT date, home_team, away_team, home_goals, away_goals
        FROM matches
        WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL
        """,
        conn
    )
    conn.close()

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    return df


class TeamResolver:
    def __init__(self, df: pd.DataFrame):
        teams = set(df["home_team"].unique()) | set(df["away_team"].unique())
        self.original_teams = list(teams)
        self.normalized_map = {
            normalize_name(t): t for t in self.original_teams
        }
        self.cache = {}
        matching_teams = [t for t in self.original_teams if "real" in t.lower()]

    def resolve(self, name: str):
        if name in self.cache:
            return self.cache[name]

        norm = normalize_name(name)

        # Direct normalized match
        if norm in self.normalized_map:
            resolved = self.normalized_map[norm]
            self.cache[name] = resolved
            return resolved

        match = process.extractOne(
            norm,
            list(self.normalized_map.keys()),
            scorer=fuzz.ratio
        )

        if match and match[1] >= FUZZ_THRESHOLD:
            resolved = self.normalized_map[match[0]]
            self.cache[name] = resolved
            return resolved

        # No match
        self.cache[name] = None
        return None


def compute_team_stats(df: pd.DataFrame, resolver: TeamResolver, team_name: str):
    resolved = resolver.resolve(team_name)

    if resolved is None:
        # No historical data match
        return None

    team_matches = []

    for _, row in df.iterrows():
        if row["home_team"] == resolved:
            gf = row["home_goals"]
            ga = row["away_goals"]
        elif row["away_team"] == resolved:
            gf = row["away_goals"]
            ga = row["home_goals"]
        else:
            continue

        if gf > ga:
            res = "W"
        elif gf < ga:
            res = "L"
        else:
            res = "D"

        team_matches.append({"gf": gf, "ga": ga, "res": res})

    if not team_matches:
        return None

    last = team_matches[-WINDOW:]
    n = len(last)

    gf_avg = sum(m["gf"] for m in last) / n
    ga_avg = sum(m["ga"] for m in last) / n
    winrate = sum(1 for m in last if m["res"] == "W") / n

    return n, gf_avg, ga_avg, winrate