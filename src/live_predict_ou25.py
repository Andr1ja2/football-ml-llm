# Live Over/Under 2.5 prediction using trained model and real bookmaker odds.

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

from feature_defs import FEATURE_COLS_BTTS_OU
from live_config import MIN_EDGE_OU25, MIN_MODEL_PROB_OU25
from live_odds import prices_to_book_probs
from team_form import (
    TeamResolver,
    build_live_goal_feature_dict,
    compute_team_stats,
    load_match_history,
)

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_ou25.pkl"
MODEL = joblib.load(MODEL_PATH)

HISTORY_DF = load_match_history()
RESOLVER = TeamResolver(HISTORY_DF)

OUTCOME_ORDER = ["OVER", "UNDER"]


def build_feature_vector(home_team: str, away_team: str) -> np.ndarray | None:
    home_stats = compute_team_stats(HISTORY_DF, RESOLVER, home_team)
    away_stats = compute_team_stats(HISTORY_DF, RESOLVER, away_team)

    if home_stats is None or away_stats is None:
        return None

    features = build_live_goal_feature_dict(home_stats, away_stats)
    values = [features[col] for col in FEATURE_COLS_BTTS_OU]
    return np.array(values).reshape(1, -1)


def fetch_candidates(matches: list[dict] | None = None) -> list[dict]:
    """Return OU 2.5 value candidates from live match odds."""
    if matches is None:
        from live_odds import fetch_live_matches

        matches = fetch_live_matches()

    candidates: list[dict] = []

    for match in matches:
        prices = match.get("totals")
        if not prices:
            continue

        home = match["home_team"]
        away = match["away_team"]

        X = build_feature_vector(home, away)
        if X is None:
            continue

        p_over = float(MODEL.predict_proba(X)[0][1])
        model_probs = {"OVER": p_over, "UNDER": 1.0 - p_over}
        book_probs = prices_to_book_probs(prices)

        for outcome in OUTCOME_ORDER:
            model_prob = model_probs[outcome]
            book_prob = book_probs[outcome]
            odds = prices[outcome]
            edge = model_prob - book_prob
            ev = model_prob * odds - 1.0

            if edge >= MIN_EDGE_OU25 and model_prob >= MIN_MODEL_PROB_OU25:
                candidates.append({
                    "match": match["match"],
                    "date": match.get("date"),
                    "market": "OU25",
                    "outcome": outcome,
                    "model_prob": model_prob,
                    "book_prob": book_prob,
                    "odds": odds,
                    "edge": edge,
                    "ev": ev,
                })

    return sorted(candidates, key=lambda x: x["edge"], reverse=True)
