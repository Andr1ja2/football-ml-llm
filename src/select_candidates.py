# This script selects betting candidates based on model predictions and edges.
# classify_outcome function checks if the edge and model probability meet the thresholds.
from predict_1x2 import load, predict_row
import pandas as pd

MIN_EDGE = 0.05
MIN_MODEL_PROB = 0.45

def classify_outcome(outcome_data):
    edge = outcome_data["edge"]
    prob = outcome_data["model_prob"]

    if edge >= MIN_EDGE and prob >= MIN_MODEL_PROB:
        return True
    return False

def main():
    df, model = load()

    recent = df.tail(200)  # pretend these are "upcoming-like"

    candidates = []

    for _, row in recent.iterrows():
        pred = predict_row(row, model)

        for outcome, data in pred["outcomes"].items():
            if classify_outcome(data):
                candidates.append({
                    "match": pred["match"],
                    "date": pred["date"],
                    "outcome": outcome,
                    "model_prob": round(data["model_prob"], 3),
                    "book_prob": round(data["book_prob"], 3),
                    "edge": round(data["edge"], 3),
                })

    out_df = pd.DataFrame(candidates)
    print(out_df.sort_values("edge", ascending=False).head(10))

if __name__ == "__main__":
    main()

