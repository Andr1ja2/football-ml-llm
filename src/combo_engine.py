import itertools
from math import prod

# ---- CONFIG ----
MAX_LEGS = 5
MIN_EV = 0.05
MIN_COMBO_PROB = 0.05

def combo_probability(legs):
    return prod(leg["model_prob"] for leg in legs)

def combo_odds(legs):
    return prod(1.0 / leg["book_prob"] for leg in legs)

def combo_ev(prob, odds):
    return prob * odds - 1.0

def build_combos(candidates, requested_size):
    combos = []

    for legs in itertools.combinations(candidates, requested_size):
        matches = [leg["match"] for leg in legs]

        if len(matches) != len(set(matches)): # match uniqueness check (may not be needed)
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
                    "match": l["match"],
                    "outcome": l["outcome"],
                    "model_prob": round(l["model_prob"], 3),
                    "book_prob": round(l["book_prob"], 3),
                    "edge": round(l["edge"], 3),
                }
                for l in legs
            ],
            "n_legs": requested_size,
            "combo_prob": round(prob, 4),
            "combo_odds": round(odds, 2),
            "expected_value": round(ev, 3),
        })

    return sorted(combos, key=lambda x: x["expected_value"], reverse=True)
