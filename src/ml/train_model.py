"""
train_model.py
--------------
Trains a Random Forest classifier on the featurized MPro dataset,
evaluates on the held-out test set, and saves the model + metrics.
"""

import io
import sys
import os
import json
import pickle
import time

import numpy as np

# Force UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        roc_auc_score,
        average_precision_score,
        precision_score,
        recall_score,
        f1_score,
        confusion_matrix,
        classification_report,
    )
except ImportError:
    print("ERROR: scikit-learn is not installed.  pip install scikit-learn")
    sys.exit(1)

# ── Paths ────────────────────────────────────────────────────────────────────
PROCESSED_DIR = "data/processed"
MODELS_DIR    = "models"
RESULTS_DIR   = "results"

X_TRAIN_PATH  = os.path.join(PROCESSED_DIR, "X_train.pkl")
Y_TRAIN_PATH  = os.path.join(PROCESSED_DIR, "y_train.pkl")
X_TEST_PATH   = os.path.join(PROCESSED_DIR, "X_test.pkl")
Y_TEST_PATH   = os.path.join(PROCESSED_DIR, "y_test.pkl")
META_PATH     = os.path.join(PROCESSED_DIR, "feature_metadata.json")

MODEL_OUT     = os.path.join(MODELS_DIR, "mpro_activity_rf_v1.pkl")
METRICS_OUT   = os.path.join(RESULTS_DIR, "model_metrics_v1.json")

# ── RF hyperparameters ────────────────────────────────────────────────────────
N_ESTIMATORS  = 100
CLASS_WEIGHT  = "balanced"
RANDOM_STATE  = 42
MAX_DEPTH     = None
N_JOBS        = -1

# ─────────────────────────────────────────────────────────────────────────────

def banner(text: str) -> None:
    line = "=" * 70
    print(f"\n{line}\n  {text}\n{line}")


def load_pickle(path: str):
    if not os.path.exists(path):
        print(f"FATAL: File not found: {path}")
        sys.exit(1)
    with open(path, "rb") as f:
        return pickle.load(f)


def save_pickle(obj, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=4)
    print(f"  Saved {path}  ({os.path.getsize(path) / 1024:.1f} KB)")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    # ── 1. Load data ──────────────────────────────────────────────────────────
    banner("LOADING FEATURIZED DATA")

    X_train = load_pickle(X_TRAIN_PATH)
    y_train = load_pickle(Y_TRAIN_PATH)
    X_test  = load_pickle(X_TEST_PATH)
    y_test  = load_pickle(Y_TEST_PATH)

    print(f"  X_train : {X_train.shape}  y_train : {y_train.shape}")
    print(f"  X_test  : {X_test.shape}  y_test  : {y_test.shape}")

    # Validate shapes against metadata
    with open(META_PATH) as f:
        meta = json.load(f)

    expected_features = meta["n_features"]
    feature_names     = meta["feature_names"]

    if X_train.shape[1] != expected_features:
        print(
            f"FATAL: X_train has {X_train.shape[1]} features "
            f"but metadata says {expected_features}."
        )
        sys.exit(1)
    if X_test.shape[1] != expected_features:
        print(
            f"FATAL: X_test has {X_test.shape[1]} features "
            f"but metadata says {expected_features}."
        )
        sys.exit(1)

    print(f"  Feature count matches metadata: {expected_features}  -- OK")
    print(f"  Train active/inactive : {(y_train==1).sum()} / {(y_train==0).sum()}")
    print(f"  Test  active/inactive : {(y_test==1).sum()} / {(y_test==0).sum()}")

    # ── 2. Train ──────────────────────────────────────────────────────────────
    banner("TRAINING RANDOM FOREST (baseline)")
    print(f"  n_estimators = {N_ESTIMATORS}")
    print(f"  class_weight = {CLASS_WEIGHT!r}")
    print(f"  max_depth    = {MAX_DEPTH}")
    print(f"  random_state = {RANDOM_STATE}")
    print(f"  n_jobs       = {N_JOBS}")
    print()

    rf = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        class_weight=CLASS_WEIGHT,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        n_jobs=N_JOBS,
    )

    t0 = time.time()
    rf.fit(X_train, y_train)
    elapsed = time.time() - t0
    print(f"  Training complete in {elapsed:.1f}s")

    # ── 3. Evaluate ───────────────────────────────────────────────────────────
    banner("EVALUATION ON HELD-OUT TEST SET")

    y_pred_proba = rf.predict_proba(X_test)[:, 1]
    y_pred       = rf.predict(X_test)

    roc_auc  = roc_auc_score(y_test, y_pred_proba)
    pr_auc   = average_precision_score(y_test, y_pred_proba)
    prec     = precision_score(y_test, y_pred, zero_division=0)
    rec      = recall_score(y_test, y_pred, zero_division=0)
    f1       = f1_score(y_test, y_pred, zero_division=0)
    cm       = confusion_matrix(y_test, y_pred)

    print(f"  ROC-AUC  : {roc_auc:.4f}")
    print(f"  PR-AUC   : {pr_auc:.4f}   (primary metric for imbalanced data)")
    print(f"  Precision: {prec:.4f}  (threshold=0.5)")
    print(f"  Recall   : {rec:.4f}  (threshold=0.5)")
    print(f"  F1       : {f1:.4f}  (threshold=0.5)")

    print("\n  Confusion Matrix (rows=actual, cols=predicted):")
    print(f"              Pred_Neg  Pred_Pos")
    print(f"  Actual_Neg  {cm[0,0]:>8}  {cm[0,1]:>8}")
    print(f"  Actual_Pos  {cm[1,0]:>8}  {cm[1,1]:>8}")

    tn, fp, fn, tp = cm.ravel()
    print(f"\n  TN={tn}  FP={fp}  FN={fn}  TP={tp}")

    print("\n  Classification Report:")
    print("  " + "-" * 58)
    report_lines = classification_report(
        y_test, y_pred,
        target_names=["Inactive (0)", "Active (1)"],
        zero_division=0,
    ).splitlines()
    for line in report_lines:
        print(f"  {line}")

    # Feature importance — top 10
    importances  = rf.feature_importances_
    top10_idx    = np.argsort(importances)[::-1][:10]
    top10_names  = [feature_names[i] for i in top10_idx]
    top10_values = [float(importances[i]) for i in top10_idx]

    print("\n  Top 10 Features by Impurity Importance:")
    print(f"  {'Rank':<6} {'Feature':<30} {'Importance':>12}")
    print("  " + "-" * 50)
    for rank, (name, val) in enumerate(zip(top10_names, top10_values), 1):
        bar = "#" * int(val * 500)
        print(f"  {rank:<6} {name:<30} {val:>12.6f}  {bar}")

    # ── 4 & 5. Save model + metrics ───────────────────────────────────────────
    banner("SAVING MODEL + METRICS")

    save_pickle(rf, MODEL_OUT)

    metrics = {
        "model_type"           : "RandomForestClassifier",
        "n_estimators"         : N_ESTIMATORS,
        "class_weight_balanced": True,
        "random_seed"          : RANDOM_STATE,
        "max_depth"            : MAX_DEPTH,
        "roc_auc"              : round(float(roc_auc), 6),
        "pr_auc"               : round(float(pr_auc), 6),
        "precision"            : round(float(prec), 6),
        "recall"               : round(float(rec), 6),
        "f1"                   : round(float(f1), 6),
        "confusion_matrix"     : cm.tolist(),
        "feature_importance"   : [
            {"rank": i + 1, "name": n, "importance": round(v, 8)}
            for i, (n, v) in enumerate(zip(top10_names, top10_values))
        ],
        "train_samples"        : int(len(y_train)),
        "test_samples"         : int(len(y_test)),
        "n_active_train"       : int((y_train == 1).sum()),
        "n_inactive_train"     : int((y_train == 0).sum()),
        "n_active_test"        : int((y_test == 1).sum()),
        "n_inactive_test"      : int((y_test == 0).sum()),
    }

    with open(METRICS_OUT, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Saved {METRICS_OUT}")

    # ── Final summary ─────────────────────────────────────────────────────────
    banner("BASELINE SUMMARY")
    print(f"  Model     : Random Forest (n_estimators={N_ESTIMATORS}, balanced)")
    print(f"  ROC-AUC   : {roc_auc:.4f}")
    print(f"  PR-AUC    : {pr_auc:.4f}  <-- key metric (imbalanced)")
    print(f"  F1        : {f1:.4f}")
    print(f"  Precision : {prec:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print()
    print(f"  Baseline locked in. Hyperparameter tuning can be measured against these.\n")


if __name__ == "__main__":
    main()
