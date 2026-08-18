"""
predict.py
----------
Real ML prediction module for MPro activity scoring.

Public API (called by pipeline.py / app.py):
    predict_activity(smiles_list)  -> pd.DataFrame
    demo_predict(frame)            -> pd.DataFrame   (legacy compat shim)

Running this file directly generates the pre-computed fallback file:
    results/fallback_predictions.csv
"""

import io
import sys
import os
import json
import pickle
import logging

import numpy as np
import pandas as pd

# Force UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

log = logging.getLogger(__name__)

# ── RDKit ────────────────────────────────────────────────────────────────────
try:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Descriptors, rdMolDescriptors, AllChem
    RDLogger.DisableLog("rdApp.*")
    _RDKIT_OK = True
except ImportError:
    _RDKIT_OK = False

# ── Paths ────────────────────────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_DIR, "..", ".."))

MODEL_PATH    = os.path.join(_ROOT, "models", "mpro_activity_rf_v1.pkl")
META_PATH     = os.path.join(_ROOT, "data", "processed", "feature_metadata.json")
LABELED_CSV   = os.path.join(_ROOT, "data", "raw", "mpro_labeled_smiles.csv")
FALLBACK_OUT  = os.path.join(_ROOT, "results", "fallback_predictions.csv")

MODEL_VERSION = "rf_v1"
ACTIVE_THRESHOLD = 0.5

# Morgan FP params — must match featurize.py exactly
MORGAN_RADIUS = 2
MORGAN_BITS   = 2048
USE_CHIRALITY = False

# ─────────────────────────────────────────────────────────────────────────────
# Lazy-loaded singletons (loaded once per process)
# ─────────────────────────────────────────────────────────────────────────────

_model = None
_feature_names = None


def _load_model():
    global _model, _feature_names
    if _model is not None:
        return _model, _feature_names

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}.\n"
            "Run src/ml/train_model.py first."
        )
    with open(MODEL_PATH, "rb") as f:
        _model = pickle.load(f)

    with open(META_PATH) as f:
        meta = json.load(f)
    _feature_names = meta["feature_names"]

    return _model, _feature_names


# ─────────────────────────────────────────────────────────────────────────────
# Featurisation (mirrors featurize.py — kept self-contained for portability)
# ─────────────────────────────────────────────────────────────────────────────

def _featurize_mol(mol) -> np.ndarray:
    """Morgan FP (2048 bits) + 6 descriptors -> float32 (2054,)."""
    fp = AllChem.GetMorganFingerprintAsBitVect(
        mol,
        radius=MORGAN_RADIUS,
        nBits=MORGAN_BITS,
        useChirality=USE_CHIRALITY,
    )
    fp_arr = np.zeros(MORGAN_BITS, dtype=np.float32)
    fp_arr[list(fp.GetOnBits())] = 1.0

    desc_arr = np.array([
        Descriptors.ExactMolWt(mol),
        Descriptors.MolLogP(mol),
        Descriptors.TPSA(mol),
        rdMolDescriptors.CalcNumHBD(mol),
        rdMolDescriptors.CalcNumHBA(mol),
        rdMolDescriptors.CalcNumRotatableBonds(mol),
    ], dtype=np.float32)

    return np.concatenate([fp_arr, desc_arr])


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def predict_activity(smiles_list: list[str]) -> pd.DataFrame:
    """
    Predict MPro activity for a list of SMILES strings.

    Parameters
    ----------
    smiles_list : list[str]
        Raw SMILES strings to score.

    Returns
    -------
    pd.DataFrame with columns:
        smiles, predicted_activity_score, predicted_class, model_version

    SMILES that fail to parse are logged and omitted from the output.
    """
    if not _RDKIT_OK:
        raise ImportError("RDKit is required for prediction. pip install rdkit")

    model, _ = _load_model()

    rows       = []
    n_failed   = 0
    feat_batch = []
    valid_smiles = []

    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi) if smi else None
        if mol is None:
            log.warning("Could not parse SMILES (skipped): %s", smi)
            n_failed += 1
            continue
        feat_batch.append(_featurize_mol(mol))
        valid_smiles.append(smi)

    if feat_batch:
        X = np.vstack(feat_batch)                    # (n_valid, 2054)
        scores = model.predict_proba(X)[:, 1]        # P(Active)

        for smi, score in zip(valid_smiles, scores):
            rows.append({
                "smiles"                   : smi,
                "predicted_activity_score" : round(float(score), 6),
                "predicted_class"          : "Active" if score >= ACTIVE_THRESHOLD else "Inactive",
                "model_version"            : MODEL_VERSION,
            })

    if n_failed:
        log.warning("%d SMILES failed to parse and were skipped.", n_failed)

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Legacy compatibility shim (used by older pipeline.py / app.py code)
# ─────────────────────────────────────────────────────────────────────────────

def demo_predict(frame: pd.DataFrame) -> pd.DataFrame:
    """
    Drop-in replacement for the old hash-based demo_predict().
    Expects a DataFrame with a 'smiles' column (or falls back to compound_id
    hash scoring if SMILES or model are unavailable).
    """
    import hashlib

    def _hash_score(compound_id: str) -> float:
        digest = hashlib.sha256(compound_id.encode()).hexdigest()
        return round(0.60 + int(digest[:8], 16) / 0xFFFFFFFF * 0.38, 4)

    # Try real prediction if smiles column exists and model is present
    if "smiles" in frame.columns and os.path.exists(MODEL_PATH) and _RDKIT_OK:
        try:
            preds = predict_activity(frame["smiles"].tolist())
            output = frame.copy().reset_index(drop=True)
            output["activity_score"]  = preds["predicted_activity_score"].values
            output["predicted_class"] = preds["predicted_class"].str.lower().values
            output["model_version"]   = MODEL_VERSION
            return output.sort_values("activity_score", ascending=False).reset_index(drop=True)
        except Exception as e:
            log.warning("Real prediction failed (%s); falling back to hash scores.", e)

    # Fallback: hash-based demo scores (original behaviour)
    output = frame.copy()
    output["activity_score"] = output["compound_id"].map(_hash_score)
    output["predicted_class"] = output["activity_score"].ge(0.75).map(
        {True: "active", False: "lower_priority"}
    )
    output["model_version"] = "demo_v1_fallback"
    return output.sort_values("activity_score", ascending=False).reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# __main__: generate fallback_predictions.csv
# ─────────────────────────────────────────────────────────────────────────────

def _banner(text: str) -> None:
    line = "=" * 70
    print(f"\n{line}\n  {text}\n{line}")


def generate_fallback():
    _banner("GENERATING FALLBACK PREDICTIONS")

    if not os.path.exists(LABELED_CSV):
        print(f"ERROR: {LABELED_CSV} not found. Run prepare_dataset.py first.")
        sys.exit(1)

    df = pd.read_csv(LABELED_CSV)
    print(f"  Loaded {len(df)} compounds from {LABELED_CSV}")

    # Run prediction
    preds = predict_activity(df["smiles"].tolist())
    n_parse_fail = len(df) - len(preds)

    # Merge back with compound_id and true_label
    # predict_activity preserves order for successfully parsed SMILES
    df_ok = df[df["smiles"].isin(preds["smiles"].values)].copy()
    df_ok = df_ok.reset_index(drop=True)
    preds = preds.reset_index(drop=True)

    output = pd.DataFrame({
        "compound_id"               : df_ok["compound_id"],
        "smiles"                    : preds["smiles"],
        "predicted_activity_score"  : preds["predicted_activity_score"],
        "predicted_class"           : preds["predicted_class"],
        "true_label"                : df_ok["activity_label"],
        "model_version"             : preds["model_version"],
    })

    os.makedirs(os.path.dirname(FALLBACK_OUT), exist_ok=True)
    output.to_csv(FALLBACK_OUT, index=False)

    # Summary
    n_predicted_active = (output["predicted_class"] == "Active").sum()
    _banner("SUMMARY")
    print(f"  Total compounds input           : {len(df)}")
    print(f"  SMILES parse failures           : {n_parse_fail}  (should be 0)")
    print(f"  Compounds predicted Active      : {n_predicted_active}")
    print(f"  Compounds predicted Inactive    : {len(output) - n_predicted_active}")
    print(f"  Fallback predictions saved to   : {FALLBACK_OUT}")
    print()


if __name__ == "__main__":
    generate_fallback()
