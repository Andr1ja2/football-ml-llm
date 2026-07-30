# Trains Over/Under 2.5 prediction models, compares candidates, and saves the production model.

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import (
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss

from feature_defs import FEATURE_COLS_BTTS_OU

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "train_btts_ou.csv"
MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "model_ou25.pkl"
CALIBRATION_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "calibration_ou25.png"

TARGET_COL = "OVER_2_5"

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
# written to model_ou25.pkl and used by the prediction pipeline.
# Change this value if you want to deploy a different benchmarked model.
PRODUCTION_MODEL_NAME = "GradientBoostingClassifier"


def load_data() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df = df.dropna(subset=FEATURE_COLS_BTTS_OU + [TARGET_COL]).copy()

    X = df[FEATURE_COLS_BTTS_OU].values
    y = df[TARGET_COL].values

    return df, X, y


def evaluate_model(name: str, model, X_train, X_test, y_train, y_test) -> dict[str, float]:
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    return {
        "model": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "log_loss": log_loss(y_test, y_proba),
        "brier_score": brier_score_loss(y_test, y_proba),
    }


def save_calibration_plot(y_true: np.ndarray, y_proba: np.ndarray, path: Path) -> None:
    frac_pos, mean_pred = calibration_curve(
        y_true,
        y_proba,
        n_bins=10,
        strategy="uniform",
    )

    fig, ax = plt.subplots(figsize=(6, 6))

    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.plot(mean_pred, frac_pos, "o-", label="Model")

    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Observed frequency")
    ax.set_title("Over/Under 2.5 Model Calibration")

    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)

    print(f"Saved calibration plot to {path}")


def main() -> None:
    df, X, y = load_data()

    print(f"Dataset rows: {len(df)}, features: {len(FEATURE_COLS_BTTS_OU)}")

    split_idx = int(len(df) * TRAIN_FRACTION)

    X_train = X[:split_idx]
    X_test = X[split_idx:]

    y_train = y[:split_idx]
    y_test = y[split_idx:]

    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    results: list[dict[str, float]] = []
    fitted_models: dict[str, object] = {}

    for name, candidate in MODEL_CANDIDATES.items():
        print(f"\nTraining {name}...")

        metrics = evaluate_model(
            name,
            candidate,
            X_train,
            X_test,
            y_train,
            y_test,
        )

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
        production_logloss = results_df.loc[
            results_df["model"] == PRODUCTION_MODEL_NAME,
            "log_loss",
        ].iloc[0]

        print(
            f"Note: production model remains "
            f"{PRODUCTION_MODEL_NAME} "
            f"(log-loss={production_logloss:.4f})"
        )

    production_model = fitted_models[PRODUCTION_MODEL_NAME]

    y_proba = production_model.predict_proba(X_test)[:, 1]

    save_calibration_plot(
        y_test,
        y_proba,
        CALIBRATION_PATH,
    )

    joblib.dump(
        production_model,
        MODEL_PATH,
    )

    print(
        f"\nSaved production model "
        f"({PRODUCTION_MODEL_NAME}) "
        f"to {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()
