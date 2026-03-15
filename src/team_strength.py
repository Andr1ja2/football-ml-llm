import pandas as pd
from collections import defaultdict

WINDOW = 5


def compute_team_strength(df: pd.DataFrame):

    df = df.sort_values("date").reset_index(drop=True)

    team_hist = defaultdict(list)

    home_attack = []
    home_defense = []

    away_attack = []
    away_defense = []

    for _, row in df.iterrows():

        home = row["home_team"]
        away = row["away_team"]

        def get_stats(team):
            hist = team_hist[team][-WINDOW:]

            if not hist:
                return 1.0, 1.0

            avg_scored = sum(h["gf"] for h in hist) / len(hist)
            avg_conceded = sum(h["ga"] for h in hist) / len(hist)

            return avg_scored, avg_conceded

        h_att, h_def = get_stats(home)
        a_att, a_def = get_stats(away)

        home_attack.append(h_att)
        home_defense.append(h_def)

        away_attack.append(a_att)
        away_defense.append(a_def)

        hg = row["home_goals"]
        ag = row["away_goals"]

        team_hist[home].append({"gf": hg, "ga": ag})
        team_hist[away].append({"gf": ag, "ga": hg})

    df["home_attack_strength"] = home_attack
    df["home_defense_strength"] = home_defense

    df["away_attack_strength"] = away_attack
    df["away_defense_strength"] = away_defense

    return df
