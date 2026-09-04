# Live 1X2 prediction using trained model and real bookmaker odds.

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from feature_defs import FEATURE_COLS_1X2
from live_config import MIN_EDGE_1X2_HOME
from live_odds import fetch_live_matches, prices_to_book_probs
from team_form import TeamResolver, build_live_feature_dict, compute_team_stats, load_match_history

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_1x2.pkl"
MODEL = joblib.load(MODEL_PATH)

HISTORY_DF = load_match_history()
RESOLVER = TeamResolver(HISTORY_DF)

LABELS = ["HOME", "DRAW", "AWAY"]


def build_feature_vector(home_team: str, away_team: str, book_probs: list[float]) -> np.ndarray | None:
    home_stats = compute_team_stats(HISTORY_DF, RESOLVER, home_team)
    away_stats = compute_team_stats(HISTORY_DF, RESOLVER, away_team)

    if home_stats is None or away_stats is None:
        return None

    features = build_live_feature_dict(home_stats, away_stats, book_probs)
    values = [features[col] for col in FEATURE_COLS_1X2]
    return np.array(values).reshape(1, -1)


def fetch_candidates(matches: list[dict] | None = None) -> list[dict]:
    """Return 1X2 value candidates from live match odds."""
    if matches is None:
        matches = fetch_live_matches()

    candidates: list[dict] = []

    for match in matches:
        prices = match.get("h2h")
        if not prices:
            continue

        home = match["home_team"]
        away = match["away_team"]

        book_probs_list = [prices_to_book_probs(prices)[label] for label in LABELS]

        X = build_feature_vector(home, away, book_probs_list)
        if X is None:
            continue

        model_probs = MODEL.predict_proba(X)[0]
        book_probs = prices_to_book_probs(prices)

        for i, label in enumerate(LABELS):
            model_prob = float(model_probs[i])
            book_prob = book_probs[label]
            odds = prices[label]
            edge = model_prob - book_prob
            ev = model_prob * odds - 1.0

            # Preserve existing 1X2 behavior: HOME bets with edge >= 0.06
            if label == "HOME" and edge >= MIN_EDGE_1X2_HOME:
                candidates.append({
                    "match": match["match"],
                    "date": match.get("date"),
                    "market": "1X2",
                    "outcome": label,
                    "model_prob": model_prob,
                    "book_prob": book_prob,
                    "odds": odds,
                    "edge": edge,
                    "ev": ev,
                })

    return sorted(candidates, key=lambda x: x["edge"], reverse=True)


if __name__ == "__main__":
    cands = fetch_candidates()
    print(f"Collected {len(cands)} 1X2 value candidates")
    for c in cands[:10]:
        print(c)
