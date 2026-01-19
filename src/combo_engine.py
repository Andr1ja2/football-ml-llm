import itertools
from math import prod

# ---- CONFIG ----
MIN_LEGS = 2
MAX_LEGS = 4
MIN_EV = 0.05          # minimum expected value
MIN_COMBO_PROB = 0.05  # avoid ultra-lottery combos

def combo_probability(legs):
    return prod(leg["model_prob"] for leg in legs)

def combo_odds(legs):
    return prod(1.0 / leg["book_prob"] for leg in legs)

def combo_ev(prob, odds):
    return prob * odds - 1.0

def build_combos(candidates):
    """
    candidates: list of dicts with keys:
      match, outcome, model_prob, book_prob, edge
    """
    combos = []

    for k in range(MIN_LEGS, MAX_LEGS + 1):
        for legs in itertools.combinations(candidates, k):
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
                        "match": l["match"],
                        "outcome": l["outcome"],
                        "model_prob": round(l["model_prob"], 3),
                        "book_prob": round(l["book_prob"], 3),
                        "edge": round(l["edge"], 3),
                    }
                    for l in legs
                ],
                "n_legs": len(legs),
                "combo_prob": round(prob, 4),
                "combo_odds": round(odds, 2),
                "expected_value": round(ev, 3),
            })

    return sorted(combos, key=lambda x: x["expected_value"], reverse=True)
