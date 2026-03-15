from live_predict_1x2 import fetch_candidates as fetch_1x2

def get_live_candidates():

    candidates = []

    # 1X2 candidates
    one_x_two = fetch_1x2()

    for c in one_x_two:

        candidates.append({
            "match": c["match"],
            "market": "1X2",
            "outcome": c["outcome"],
            "model_prob": c["model_prob"],
            "book_prob": c["book_prob"],
            "edge": c.get("edge", 0),
            "ev": c.get("ev", 0),
        })

    return candidates
