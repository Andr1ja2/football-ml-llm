# collect_candidates function takes a dataframe of matches and a trained model for 1X2 predictions, 
# and returns a list of all valid betting candidates with their respective edges and probabilities
# main function prints the top combinations based on expected value.
from select_candidates import load, predict_row
from combo_engine import build_combos, MAX_LEGS
from predict_btts import load as load_btts, predict_row as predict_btts
from predict_ou25 import load as load_ou, predict_row as predict_ou
from fixture_adapter import load_fixtures
from live_candidates import get_live_candidates

def collect_candidates(df, model_1x2):
    btts_df, btts_model = load_btts()
    ou_df, ou_model = load_ou()

    recent = df.tail(200)
    candidates = []

    for _, row in recent.iterrows():
        pred = predict_row(row, model_1x2)

        # 1X2
        labels = ["HOME", "DRAW", "AWAY"]

        model_probs = [
            pred["outcomes"]["HOME"]["model_prob"],
            pred["outcomes"]["DRAW"]["model_prob"],
            pred["outcomes"]["AWAY"]["model_prob"],
        ]

        book_probs = [
            pred["outcomes"]["HOME"]["book_prob"],
            pred["outcomes"]["DRAW"]["book_prob"],
            pred["outcomes"]["AWAY"]["book_prob"],
        ]

        for i, outcome in enumerate(labels):

            model_prob = model_probs[i]
            book_prob = book_probs[i]

            odds = 1 / (book_prob * 1.05)

            EV = model_prob * odds - 1

            # only home bets with EV >= 0.06
            if outcome == "HOME" and EV >= 0.06:

                candidates.append({
                    "match": pred["match"],
                    "market": "1X2",
                    "outcome": outcome,
                    "model_prob": model_prob,
                    "book_prob": book_prob,
                    "edge": EV,
                    "ev": EV,
                })

        # BTTS
        btts_row = btts_df.loc[btts_df["match_id"] == row["match_id"]]
        if not btts_row.empty:
            probs = predict_btts(btts_row.iloc[0], btts_model)
            for o, p in probs.items():
                book = 0.5
                edge = p - book
                if edge >= 0.05 and p >= 0.45:
                    candidates.append({
                        "match": pred["match"],
                        "market": "BTTS",
                        "outcome": o,
                        "model_prob": p,
                        "book_prob": book,
                        "edge": edge,
                    })

        # OU 2.5
        ou_row = ou_df.loc[ou_df["match_id"] == row["match_id"]]
        if not ou_row.empty:
            probs = predict_ou(ou_row.iloc[0], ou_model)
            for o, p in probs.items():
                book = 0.5
                edge = p - book
                if edge >= 0.05 and p >= 0.45:
                    candidates.append({
                        "match": pred["match"],
                        "market": "OU25",
                        "outcome": o,
                        "model_prob": p,
                        "book_prob": book,
                        "edge": edge,
                    })

    return candidates

def main(requested_size, return_objects=False):
    was_capped = False
    if requested_size > MAX_LEGS:
        requested_size = MAX_LEGS
        was_capped = True

    candidates = get_live_candidates()
    
    combos = build_combos(candidates, requested_size)

    if return_objects:
        return combos, was_capped

    print(f"\nTop {requested_size}-selection combos:\n")
    for c in combos[:5]:
        print(f"{c['n_legs']} selections | EV={c['expected_value']} | odds={c['combo_odds']}")
        for leg in c["legs"]:
            print(f"  - {leg['match']} [{leg['outcome']}] edge={leg['edge']}")
        print()
        
