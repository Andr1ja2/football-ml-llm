# Combo engine: combine value candidates into multi-leg tickets.
#
# Combined probability is computed as the product of individual model
# probabilities. This assumes leg outcomes are independent approximation
# that ignores correlation (e.g. a high-scoring match affects both BTTS and OU).

from __future__ import annotations

import itertools
from math import prod

# ---- CONFIG ----
# maximum number of legs in a combination, I found that my machine can handle up to 5 legs without running out of memory, but more than that may cause issues.
MAX_LEGS = 5
MIN_EV = 0.05
MIN_COMBO_PROB = 0.05


def combo_probability(legs: list[dict]) -> float:
    """Product of model probabilities (independence assumption)."""
    return prod(leg["model_prob"] for leg in legs)


def combo_odds(legs: list[dict]) -> float:
    """Product of decimal bookmaker odds when available, else implied from book_prob."""
    odds_values = []
    for leg in legs:
        if "odds" in leg and leg["odds"] > 0:
            odds_values.append(leg["odds"])
        elif leg.get("book_prob", 0) > 0:
            odds_values.append(1.0 / leg["book_prob"])
        else:
            return 0.0
    return prod(odds_values)


def combo_ev(prob: float, odds: float) -> float:
    return prob * odds - 1.0


def build_combos(candidates: list[dict], requested_size: int) -> list[dict]:
    combos: list[dict] = []

    for legs in itertools.combinations(candidates, requested_size):
        matches = [leg["match"] for leg in legs]

        # Prevent multiple selections from the same match
        if len(matches) != len(set(matches)):
            continue

        prob = combo_probability(legs)
        odds = combo_odds(legs)
        ev = combo_ev(prob, odds)

        if prob < MIN_COMBO_PROB:
            continue
        if ev < MIN_EV:
            continue

        combos.append({
            "legs": [
                {
                    "match": leg["match"],
                    "market": leg.get("market", ""),
                    "outcome": leg["outcome"],
                    "model_prob": round(leg["model_prob"], 3),
                    "book_prob": round(leg["book_prob"], 3),
                    "odds": round(leg.get("odds", 0), 2),
                    "edge": round(leg["edge"], 3),
                }
                for leg in legs
            ],
            "n_legs": requested_size,
            "combo_prob": round(prob, 4),
            "combo_odds": round(odds, 2),
            "expected_value": round(ev, 3),
        })

    return sorted(combos, key=lambda x: x["expected_value"], reverse=True)
