# This script fetches live odds data from the Odds API for various soccer leagues and 
# processes it to create a list of betting candidates with normalized probabilities.
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")

SPORTS = [
    "soccer_epl",
    "soccer_germany_bundesliga",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
]

BASE_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"


def decimal_to_prob(odds):
    return 1.0 / odds if odds > 0 else 0


def normalize_probs(probs):
    total = sum(probs)
    if total == 0:
        return probs
    return [p / total for p in probs]


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
            prices = [o["price"] for o in outcomes]
            raw_probs = [decimal_to_prob(p) for p in prices]
            norm_probs = normalize_probs(raw_probs)

            labels = ["HOME", "DRAW", "AWAY"]

            for i in range(3):
                candidates.append({
                    "match": f"{home} vs {away}",
                    "market": "1X2",
                    "outcome": labels[i],
                    "model_prob": norm_probs[i],   # placeholder until model
                    "book_prob": norm_probs[i],
                    "edge": 0.0,
                })

    return candidates


if __name__ == "__main__":
    cands = fetch_candidates()
    print(f"Collected {len(cands)} candidates")
    for c in cands[:10]:
        print(c)
