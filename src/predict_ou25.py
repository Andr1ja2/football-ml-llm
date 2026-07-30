# Over/Under 2.5 prediction helpers — feature column order matches training exactly.

from pathlib import Path

import joblib
import pandas as pd

from feature_defs import FEATURE_COLS_BTTS_OU

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_btts_ou.csv"
MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_ou25.pkl"


def predict_row(row, model):
    X = row[FEATURE_COLS_BTTS_OU].values.reshape(1, -1)
    p_over = model.predict_proba(X)[0][1]
    return {
        "OVER": p_over,
        "UNDER": 1 - p_over,
    }


def load():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values("date")
    model = joblib.load(MODEL_PATH)
    return df, model
