from pathlib import Path
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import train_test_split

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_1x2.csv"

def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    feature_cols = [
        "home_prob",
        "draw_prob",
        "away_prob",
        "home_matches_played",
        "home_avg_gf",
        "home_avg_ga",
        "home_winrate",
        "away_matches_played",
        "away_avg_gf",
        "away_avg_ga",
        "away_winrate",
    ]
    X = df[feature_cols].values
    y = df["label_1x2"].values
    return df, X, y

def main():
    df, X, y = load_data()

    # Sort by date
    df = df.sort_values("date").reset_index(drop=True)

    feature_cols = [
        "home_prob",
        "draw_prob",
        "away_prob",
        "home_matches_played",
        "home_avg_gf",
        "home_avg_ga",
        "home_winrate",
        "away_matches_played",
        "away_avg_gf",
        "away_avg_ga",
        "away_winrate",
    ]

    # Drop any rows with NaNs in feature columns or label
    before = len(df)
    df = df.dropna(subset=feature_cols + ["label_1x2"]).copy()
    after = len(df)
    print(f"Dropped {before - after} rows with NaNs, remaining: {after}")

    X = df[feature_cols].values
    y = df["label_1x2"].values

    # 80% oldest matches as train, 20% newest as test
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    model = GradientBoostingClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    ll = log_loss(y_test, y_proba)

    print(f"Test accuracy: {acc:.3f}")
    print(f"Test log-loss: {ll:.3f}")

        # Save model for later use
    model_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_1x2.pkl"
    joblib.dump(model, model_path)
    print(f"Saved model to {model_path}")


if __name__ == "__main__":
    main()
