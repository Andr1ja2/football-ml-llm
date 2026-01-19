import pandas as pd
import joblib
from pathlib import Path
import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_btts_ou.csv"
MODEL = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_btts.pkl"

FEATURES = [
    "home_btts_rate",
    "home_avg_goals",
    "away_btts_rate",
    "away_avg_goals",
]

def predict_row(row, model):
    X = row[FEATURES].values.reshape(1, -1)
    p_yes = model.predict_proba(X)[0][1]
    return {
        "YES": p_yes,
        "NO": 1 - p_yes
    }

def load():
    df = pd.read_csv(DATA, parse_dates=["date"]).sort_values("date")
    model = joblib.load(MODEL)
    return df, model
