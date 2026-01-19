import pandas as pd
import joblib
from pathlib import Path
import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_btts_ou.csv"
MODEL = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_ou25.pkl"

FEATURES = [
    "home_avg_goals",
    "away_avg_goals",
    "home_btts_rate",
    "away_btts_rate",
]

def predict_row(row, model):
    X = row[FEATURES].values.reshape(1, -1)
    p_over = model.predict_proba(X)[0][1]
    return {
        "OVER": p_over,
        "UNDER": 1 - p_over
    }

def load():
    df = pd.read_csv(DATA, parse_dates=["date"]).sort_values("date")
    model = joblib.load(MODEL)
    return df, model
