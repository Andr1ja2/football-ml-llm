# Trains 1X2 outcome models, compares candidates, and saves the production model.
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

from feature_defs import FEATURE_COLS_1X2

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_1x2.csv"
MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_1x2.pkl"
CALIBRATION_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "calibration_1x2.png"

TRAIN_FRACTION = 0.8
RANDOM_STATE = 42

MODEL_CANDIDATES: dict[str, object] = {
    "GradientBoostingClassifier": GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=2,
        subsample=1.0,
        max_features="sqrt",
        random_state=RANDOM_STATE,
    ),
    "LogisticRegression": LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
    ),
    "RandomForestClassifier": RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
    "HistGradientBoostingClassifier": HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.1,
        max_depth=4,
        random_state=RANDOM_STATE,
    ),
}

# Production model to save after benchmarking.
# All candidate models are trained and evaluated, but only this model is
# written to model_1x2.pkl and used by the prediction pipeline.
# Change this value if you want to deploy a different benchmarked model.
PRODUCTION_MODEL_NAME = "GradientBoostingClassifier"


def load_data() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df = df.dropna(subset=FEATURE_COLS_1X2 + ["label_1x2"]).copy()
    X = df[FEATURE_COLS_1X2].values
    y = df["label_1x2"].values
    return df, X, y


def multiclass_brier_score(y_true: np.ndarray, y_proba: np.ndarray) -> float:
    n_classes = y_proba.shape[1]
    y_onehot = np.zeros((len(y_true), n_classes))
    y_onehot[np.arange(len(y_true)), y_true.astype(int)] = 1
    return float(np.mean(np.sum((y_proba - y_onehot) ** 2, axis=1)))


def evaluate_model(name: str, model, X_train, X_test, y_train, y_test) -> dict[str, float]:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    return {
        "model": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "log_loss": log_loss(y_test, y_proba),
        "brier_score": multiclass_brier_score(y_test, y_proba),
    }


def save_calibration_plot(y_true: np.ndarray, y_proba: np.ndarray, path: Path) -> None:
    """Reliability diagram using max predicted probability vs empirical accuracy."""
    confidences = y_proba.max(axis=1)
    predictions = y_proba.argmax(axis=1)
    correct = (predictions == y_true).astype(float)

    bins = np.linspace(0, 1, 11)
    bin_centers = []
    bin_accs = []

    for low, high in zip(bins[:-1], bins[1:]):
        mask = (confidences >= low) & (confidences < high)
        if mask.sum() == 0:
            continue
        bin_centers.append(confidences[mask].mean())
        bin_accs.append(correct[mask].mean())

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.plot(bin_centers, bin_accs, "o-", label="Model")
    ax.set_xlabel("Mean predicted confidence")
    ax.set_ylabel("Fraction of correct predictions")
    ax.set_title("1X2 Model Calibration")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print(f"Saved calibration plot to {path}")


def main() -> None:
    df, X, y = load_data()
    print(f"Dataset rows: {len(df)}, features: {len(FEATURE_COLS_1X2)}")

    split_idx = int(len(df) * TRAIN_FRACTION)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    results = []
    fitted_models: dict[str, object] = {}

    for name, candidate in MODEL_CANDIDATES.items():
        print(f"\nTraining {name}...")
        metrics = evaluate_model(name, candidate, X_train, X_test, y_train, y_test)
        results.append(metrics)
        fitted_models[name] = candidate
        print(
            f"  accuracy={metrics['accuracy']:.3f}  "
            f"log_loss={metrics['log_loss']:.3f}  "
            f"brier={metrics['brier_score']:.3f}"
        )

    results_df = pd.DataFrame(results).sort_values("log_loss")
    print("\n=== Model Comparison (sorted by log-loss, lower is better) ===")
    print(results_df.to_string(index=False, float_format="%.4f"))

    best = results_df.iloc[0]
    print(f"\nBest model by log-loss: {best['model']}")
    if best["model"] != PRODUCTION_MODEL_NAME:
        print(
            f"Note: production model remains {PRODUCTION_MODEL_NAME} "
            f"(log-loss={results_df.loc[results_df['model']==PRODUCTION_MODEL_NAME, 'log_loss'].iloc[0]:.4f})"
        )

    production_model = fitted_models[PRODUCTION_MODEL_NAME]
    y_proba = production_model.predict_proba(X_test)
    save_calibration_plot(y_test, y_proba, CALIBRATION_PATH)

    joblib.dump(production_model, MODEL_PATH)
    print(f"\nSaved production model ({PRODUCTION_MODEL_NAME}) to {MODEL_PATH}")


if __name__ == "__main__":
    main()
