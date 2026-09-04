# Live BTTS prediction using trained model and real bookmaker odds.

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from feature_defs import FEATURE_COLS_BTTS_OU
from live_config import MIN_EDGE_BTTS, MIN_MODEL_PROB_BTTS
from live_odds import prices_to_book_probs
from team_form import (
    TeamResolver,
    build_live_goal_feature_dict,
    compute_team_stats,
    load_match_history,
)

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_btts.pkl"
MODEL = joblib.load(MODEL_PATH)

HISTORY_DF = load_match_history()
RESOLVER = TeamResolver(HISTORY_DF)

OUTCOME_ORDER = ["YES", "NO"]


def build_feature_vector(home_team: str, away_team: str) -> np.ndarray | None:
    home_stats = compute_team_stats(HISTORY_DF, RESOLVER, home_team)
    away_stats = compute_team_stats(HISTORY_DF, RESOLVER, away_team)

    if home_stats is None or away_stats is None:
        return None

    features = build_live_goal_feature_dict(home_stats, away_stats)
    values = [features[col] for col in FEATURE_COLS_BTTS_OU]
    return np.array(values).reshape(1, -1)


def fetch_candidates(matches: list[dict] | None = None) -> list[dict]:
    """Return BTTS value candidates from live match odds."""
    if matches is None:
        from live_odds import fetch_live_matches

        matches = fetch_live_matches()

    candidates: list[dict] = []

    for match in matches:
        prices = match.get("btts")
        if not prices:
            continue

        home = match["home_team"]
        away = match["away_team"]

        X = build_feature_vector(home, away)
        if X is None:
            continue

        p_yes = float(MODEL.predict_proba(X)[0][1])
        model_probs = {"YES": p_yes, "NO": 1.0 - p_yes}
        book_probs = prices_to_book_probs(prices)

        for outcome in OUTCOME_ORDER:
            model_prob = model_probs[outcome]
            book_prob = book_probs[outcome]
            odds = prices[outcome]
            edge = model_prob - book_prob
            ev = model_prob * odds - 1.0

            if edge >= MIN_EDGE_BTTS and model_prob >= MIN_MODEL_PROB_BTTS:
                candidates.append({
                    "match": match["match"],
                    "date": match.get("date"),
                    "market": "BTTS",
                    "outcome": outcome,
                    "model_prob": model_prob,
                    "book_prob": book_prob,
                    "odds": odds,
                    "edge": edge,
                    "ev": ev,
                })

    return sorted(candidates, key=lambda x: x["edge"], reverse=True)
