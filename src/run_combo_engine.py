from select_candidates import load, predict_row
from combo_engine import build_combos, MAX_LEGS
from predict_btts import load as load_btts, predict_row as predict_btts
from predict_ou25 import load as load_ou, predict_row as predict_ou

def collect_candidates(df, model_1x2):
    btts_df, btts_model = load_btts()
    ou_df, ou_model = load_ou()

    recent = df.tail(200)
    candidates = []

    for _, row in recent.iterrows():
        pred = predict_row(row, model_1x2)

        # 1X2
        for outcome, data in pred["outcomes"].items():
            if data["edge"] >= 0.05 and data["model_prob"] >= 0.45:
                candidates.append({
                    "match": pred["match"],
                    "outcome": outcome,
                    "model_prob": data["model_prob"],
                    "book_prob": data["book_prob"],
                    "edge": data["edge"],
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
                        "outcome": o,
                        "model_prob": p,
                        "book_prob": book,
                        "edge": edge,
                    })

    return candidates

def main(requested_size, return_objects=False):
    df, model = load()

    was_capped = False
    if requested_size > MAX_LEGS:
        requested_size = MAX_LEGS
        was_capped = True

    candidates = collect_candidates(df, model)
    combos = build_combos(candidates, requested_size)

    if return_objects:
        return combos, was_capped

    print(f"\nTop {requested_size}-selection combos:\n")
    for c in combos[:5]:
        print(f"{c['n_legs']} selections | EV={c['expected_value']} | odds={c['combo_odds']}")
        for leg in c["legs"]:
            print(f"  - {leg['match']} [{leg['outcome']}] edge={leg['edge']}")
        print()
        