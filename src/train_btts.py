import pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import log_loss
import joblib

DATA = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_btts_ou.csv"
OUT = Path(__file__).resolve().parent.parent / "data" / "processed"

FEATURES = [
    "home_btts_rate",
    "home_avg_goals",
    "away_btts_rate",
    "away_avg_goals"
]

def main():
    df = pd.read_csv(DATA, parse_dates=["date"])
    df = df.sort_values("date")

    X = df[FEATURES].values
    y = df["BTTS"].values

    split = int(len(df) * 0.8)
    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]

    model = GradientBoostingClassifier()
    model.fit(X_tr, y_tr)

    probs = model.predict_proba(X_te)
    ll = log_loss(y_te, probs)

    print(f"BTTS log-loss: {ll:.3f}")

    joblib.dump(model, OUT / "model_btts.pkl")

if __name__ == "__main__":
    main()
