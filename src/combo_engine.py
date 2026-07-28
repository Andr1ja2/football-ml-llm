# build_combos generates every possible ticket combination of a given size from a list of betting candidates, 
# calculates the probability, odds, and expected value for each combination, and filters out combinations that do not meet specified thresholds. 
# It returns a sorted list of valid combinations based on expected value.
import itertools
from math import prod

# ---- CONFIG ----
# maximum number of legs in a combination, I found that my machine can handle up to 5 legs without running out of memory, but more than that may cause issues.
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
