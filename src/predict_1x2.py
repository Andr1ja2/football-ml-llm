# predict_row function takes a one match feature vector as input
# it outputs a dictionary with home probs, draw probs, away probs, and edges for each outcome
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from feature_defs import FEATURE_COLS_1X2

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_1x2.csv"
MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_1x2.pkl"

OUTCOMES = ["HOME", "DRAW", "AWAY"]


def load():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    model = joblib.load(MODEL_PATH)
    return df, model


def predict_row(row, model):
    X = row[FEATURE_COLS_1X2].values.reshape(1, -1)
    model_probs = model.predict_proba(X)[0]

    book_probs = np.array([
        row["home_prob"],
        row["draw_prob"],
        row["away_prob"],
    ])

    edges = model_probs - book_probs

    result = {
        "match": f"{row['home_team']} vs {row['away_team']}",
        "date": row["date"].strftime("%Y-%m-%d"),
        "outcomes": {},
    }

    for i, name in enumerate(OUTCOMES):
        result["outcomes"][name] = {
            "book_prob": float(book_probs[i]),
            "model_prob": float(model_probs[i]),
            "edge": float(edges[i]),
        }

    return result


def pick_recent_match(df, n=1):
    return df.tail(200).sample(n)


if __name__ == "__main__":
    df, model = load()
    row = pick_recent_match(df).iloc[0]
    prediction = predict_row(row, model)

    from pprint import pprint
    pprint(prediction)
