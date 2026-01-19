import pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import log_loss
import joblib

DATA = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_btts_ou.csv"
OUT  = Path(__file__).resolve().parent.parent / "data" / "processed"

FEATURES = [
    "home_avg_goals",
    "away_avg_goals",
    "home_btts_rate",
    "away_btts_rate",
]

def main():
    df = pd.read_csv(DATA, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    X = df[FEATURES].values
    y = df["OVER_2_5"].values

    split = int(len(df) * 0.8)
    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]

    model = GradientBoostingClassifier()
    model.fit(X_tr, y_tr)

    probs = model.predict_proba(X_te)
    ll = log_loss(y_te, probs)

    print(f"O/U 2.5 log-loss: {ll:.3f}")

    joblib.dump(model, OUT / "model_ou25.pkl")
    print(f"Saved model to {OUT / 'model_ou25.pkl'}")

if __name__ == "__main__":
    main()
