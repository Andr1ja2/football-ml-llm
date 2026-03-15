import os
import requests
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from dotenv import load_dotenv
from team_form import load_match_history, compute_team_stats, TeamResolver

load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_1x2.pkl"
MODEL = joblib.load(MODEL_PATH)

SPORTS = [
    "soccer_epl",
    "soccer_germany_bundesliga",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
]

BASE_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"


HISTORY_DF = load_match_history()
RESOLVER = TeamResolver(HISTORY_DF)


def decimal_to_prob(odds):
    return 1.0 / odds if odds > 0 else 0


def normalize_probs(probs):
    total = sum(probs)
    if total == 0:
        return probs
    return [p / total for p in probs]


def build_feature_vector(home_team, away_team, book_probs):

    home_stats = compute_team_stats(HISTORY_DF, RESOLVER, home_team)
    away_stats = compute_team_stats(HISTORY_DF, RESOLVER, away_team)

    if home_stats is None or away_stats is None:
        return None

    h_n, h_gf, h_ga, h_win = home_stats
    a_n, a_gf, a_ga, a_win = away_stats

    # simple attack/defense estimation
    home_attack = h_gf
    home_defense = h_ga

    away_attack = a_gf
    away_defense = a_ga

    return np.array([
        book_probs[0],
        book_probs[1],
        book_probs[2],

        h_n,
        h_gf,
        h_ga,
        h_win,

        a_n,
        a_gf,
        a_ga,
        a_win,

        home_attack,
        away_attack,
        home_defense,
        away_defense
    ]).reshape(1, -1)


def fetch_candidates():
    candidates = []

    for sport in SPORTS:
        url = BASE_URL.format(sport=sport)

        params = {
            "apiKey": API_KEY,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal",
        }

        resp = requests.get(url, params=params)

        if resp.status_code != 200:
            print(f"Failed for {sport}: {resp.text}")
            continue

        matches = resp.json()

        for match in matches:
            home = match["home_team"]
            away = match["away_team"]

            if not match["bookmakers"]:
                continue

            book = match["bookmakers"][0]
            market = book["markets"][0]
            outcomes = market["outcomes"]

            if len(outcomes) != 3:
                continue

            # Extract odds
            home_odds = None
            draw_odds = None
            away_odds = None

            for o in outcomes:
                name = o["name"].lower().strip()

                if name == home.lower():
                    home_odds = o["price"]
                elif name == away.lower():
                    away_odds = o["price"]
                elif name == "draw":
                    draw_odds = o["price"]

            # Skip if anything missing
            if home_odds is None or draw_odds is None or away_odds is None:
                continue

            prices = [home_odds, draw_odds, away_odds]

            raw_probs = [decimal_to_prob(p) for p in prices]
            book_probs = normalize_probs(raw_probs)


            # Run model
            X = build_feature_vector(home, away, book_probs)
            if X is None:
                continue
            model_probs = MODEL.predict_proba(X)[0]
            # model_probs = np.clip(model_probs, 0.05, 0.85) # can prevent absurd values (but may be wrong)

            labels = ["HOME", "DRAW", "AWAY"]

            for i in range(3):
                edge = model_probs[i] - book_probs[i]

                if edge >= 0.03 and model_probs[i] >= 0.4: # arbitrary thresholds for value
                    candidates.append({
                        "match": f"{home} vs {away}",
                        "market": "1X2",
                        "outcome": labels[i],
                        "model_prob": float(model_probs[i]),
                        "book_prob": float(book_probs[i]),
                        "edge": float(edge),
                    })

    return candidates


if __name__ == "__main__":
    cands = fetch_candidates()
    print(f"Collected {len(cands)} value candidates")
    for c in cands[:10]:
        print(c)
