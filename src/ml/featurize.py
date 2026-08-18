"""
featurize.py
------------
Loads mpro_labeled_smiles.csv, generates Morgan fingerprint + descriptor
feature vectors, performs scaffold-based train/test split, and saves
processed arrays + metadata.
"""

import io
import sys
import os
import json
import pickle
import warnings

import numpy as np
import pandas as pd

# Force UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── RDKit imports ────────────────────────────────────────────────────────────
try:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Descriptors, rdMolDescriptors, AllChem, MolToSmiles
    from rdkit.Chem.Scaffolds import MurckoScaffold
    RDLogger.DisableLog("rdApp.*")
except ImportError:
    print("ERROR: RDKit is not installed.  pip install rdkit")
    sys.exit(1)

# ── Constants ────────────────────────────────────────────────────────────────
INPUT_CSV    = "data/raw/mpro_labeled_smiles.csv"
OUT_DIR      = "data/processed"

MORGAN_RADIUS = 2
MORGAN_BITS   = 2048
USE_CHIRALITY = False
RANDOM_SEED   = 42
TRAIN_FRAC    = 0.80

DESC_NAMES = ["mw", "logp", "tpsa", "hbd", "hba", "rotatable_bonds"]
FEATURE_NAMES = (
    [f"fingerprint_{i}" for i in range(MORGAN_BITS)]
    + DESC_NAMES
)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def banner(text: str) -> None:
    line = "=" * 70
    print(f"\n{line}\n  {text}\n{line}")


def mol_from_smiles(smiles: str, compound_id: str):
    """Parse SMILES; exit loudly on failure."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(
            f"\nFATAL: Could not parse SMILES for {compound_id}:\n  {smiles}\n"
            "The dataset must be fixed before featurisation can continue."
        )
        sys.exit(1)
    return mol


def compute_features(mol) -> np.ndarray:
    """Morgan FP (2048) + 6 descriptors -> 2054-dim float32 array."""
    # Morgan fingerprint
    fp = AllChem.GetMorganFingerprintAsBitVect(
        mol,
        radius=MORGAN_RADIUS,
        nBits=MORGAN_BITS,
        useChirality=USE_CHIRALITY,
    )
    fp_arr = np.zeros(MORGAN_BITS, dtype=np.float32)
    fp_arr[list(fp.GetOnBits())] = 1.0

    # Descriptors
    desc_arr = np.array([
        Descriptors.ExactMolWt(mol),
        Descriptors.MolLogP(mol),
        Descriptors.TPSA(mol),
        rdMolDescriptors.CalcNumHBD(mol),
        rdMolDescriptors.CalcNumHBA(mol),
        rdMolDescriptors.CalcNumRotatableBonds(mol),
    ], dtype=np.float32)

    return np.concatenate([fp_arr, desc_arr])


def murcko_scaffold(mol) -> str:
    """Return the canonical SMILES of the Murcko scaffold (empty string for linear mols)."""
    try:
        scaffold = MurckoScaffold.GetScaffoldForMol(mol)
        return MolToSmiles(scaffold, canonical=True)
    except Exception:
        return ""


def scaffold_split(df_mol: pd.DataFrame, train_frac: float, seed: int):
    """
    Group molecules by Murcko scaffold, then assign scaffold-groups to
    train/test to achieve the desired split ratio while keeping entire
    scaffold groups together (avoids data leakage).

    Returns: train_idx, test_idx  (lists of integer positional indices)
    """
    # Build scaffold -> [row indices] map
    scaffold_map: dict[str, list[int]] = {}
    for idx, row in df_mol.iterrows():
        s = row["scaffold"]
        scaffold_map.setdefault(s, []).append(idx)

    # Sort scaffold groups by size desc (deterministic + fills train first)
    groups = sorted(scaffold_map.values(), key=len, reverse=True)

    n_total    = len(df_mol)
    n_train    = int(n_total * train_frac)
    train_idx, test_idx = [], []

    rng = np.random.default_rng(seed)
    # Shuffle groups of equal size to reduce bias
    max_size = groups[0].__len__()
    rng.shuffle(groups)   # light shuffle; large groups still go to train by size sort

    # Re-sort after shuffle to keep largest first
    groups = sorted(groups, key=len, reverse=True)

    for group in groups:
        if len(train_idx) < n_train:
            train_idx.extend(group)
        else:
            test_idx.extend(group)

    return train_idx, test_idx


def ratio_str(y: np.ndarray) -> str:
    n_act = int((y == 1).sum())
    n_ina = int((y == 0).sum())
    ratio = n_act / n_ina if n_ina else float("inf")
    return f"Active={n_act}  Inactive={n_ina}  ratio={ratio:.3f}:1"


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # ── 1. Load ───────────────────────────────────────────────────────────────
    banner("LOADING DATA")
    df = pd.read_csv(INPUT_CSV)
    print(f"  Rows loaded : {len(df)}")
    print(f"  Columns     : {list(df.columns)}")
    print(f"  Label counts: {df['activity_label'].value_counts().to_dict()}")

    # ── 2. Parse SMILES + compute features ────────────────────────────────────
    banner("PARSING SMILES + COMPUTING FEATURES")
    mols       = []
    scaffolds  = []
    feat_rows  = []

    for _, row in df.iterrows():
        mol = mol_from_smiles(row["smiles"], row["compound_id"])
        mols.append(mol)
        scaffolds.append(murcko_scaffold(mol))
        feat_rows.append(compute_features(mol))

    X = np.vstack(feat_rows)                       # (2025, 2054)
    y = (df["activity_label"].str.lower() == "active").astype(np.int8).values

    df["scaffold"] = scaffolds

    print(f"  Feature matrix shape : {X.shape}")
    print(f"  Label vector shape   : {y.shape}")
    print(f"  Positives (active)   : {y.sum()}")
    print(f"  Negatives (inactive) : {(y == 0).sum()}")

    # Verify descriptor range sanity
    mw_col = X[:, MORGAN_BITS]       # first descriptor
    print(f"  MW range (sanity)    : {mw_col.min():.1f} — {mw_col.max():.1f} Da")

    # ── 3. Scaffold split ─────────────────────────────────────────────────────
    banner("SCAFFOLD-BASED TRAIN / TEST SPLIT  (80% / 20%)")
    n_scaffolds = df["scaffold"].nunique()
    print(f"  Unique Murcko scaffolds : {n_scaffolds}")
    print(f"  (singletons = linear/acyclic mols grouped under empty scaffold)")

    if n_scaffolds < 5:
        print(
            "  WARNING: Too few unique scaffolds for a meaningful scaffold split.\n"
            "  Falling back to random split (seed 42)."
        )
        rng = np.random.default_rng(RANDOM_SEED)
        idx = rng.permutation(len(df))
        n_train = int(len(df) * TRAIN_FRAC)
        train_idx = idx[:n_train].tolist()
        test_idx  = idx[n_train:].tolist()
    else:
        train_idx, test_idx = scaffold_split(df, TRAIN_FRAC, RANDOM_SEED)

    X_train, y_train = X[train_idx], y[train_idx]
    X_test,  y_test  = X[test_idx],  y[test_idx]

    # ── Ratio check ───────────────────────────────────────────────────────────
    print(f"\n  Train ({len(train_idx)} samples):  {ratio_str(y_train)}")
    print(f"  Test  ({len(test_idx)} samples):  {ratio_str(y_test)}")

    # Warn if ratio diverges by more than 2x between train and test
    train_rate = y_train.mean()
    test_rate  = y_test.mean()
    if train_rate > 0 and test_rate > 0:
        ratio_diff = max(train_rate / test_rate, test_rate / train_rate)
        if ratio_diff > 2.0:
            print(
                f"\n  WARNING: Active fraction differs significantly between train "
                f"({train_rate:.3f}) and test ({test_rate:.3f}).\n"
                "  Scaffold split may have caused label imbalance. "
                "Consider stratified random split if this is a concern."
            )

    # ── 4. Save artifacts ────────────────────────────────────────────────────
    banner("SAVING ARTIFACTS")

    def _save(obj, path: str):
        with open(path, "wb") as f:
            pickle.dump(obj, f, protocol=4)
        print(f"  Saved {path}  ({os.path.getsize(path) / 1024:.1f} KB)")

    _save(X_train, os.path.join(OUT_DIR, "X_train.pkl"))
    _save(y_train, os.path.join(OUT_DIR, "y_train.pkl"))
    _save(X_test,  os.path.join(OUT_DIR, "X_test.pkl"))
    _save(y_test,  os.path.join(OUT_DIR, "y_test.pkl"))

    metadata = {
        "feature_names"    : FEATURE_NAMES,
        "n_samples"        : int(len(df)),
        "n_features"       : int(X.shape[1]),
        "n_active_train"   : int((y_train == 1).sum()),
        "n_inactive_train" : int((y_train == 0).sum()),
        "n_active_test"    : int((y_test == 1).sum()),
        "n_inactive_test"  : int((y_test == 0).sum()),
        "random_seed"      : RANDOM_SEED,
        "train_frac"       : TRAIN_FRAC,
        "morgan_radius"    : MORGAN_RADIUS,
        "morgan_bits"      : MORGAN_BITS,
        "use_chirality"    : USE_CHIRALITY,
        "split_method"     : "scaffold_murcko",
    }
    meta_path = os.path.join(OUT_DIR, "feature_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved {meta_path}")

    # ── 5. Final summary ────────────────────────────────────────────────────
    banner("SUMMARY")
    print(f"  Total samples        : {len(df)}")
    print(f"  Feature dimensions   : {X.shape[1]}  "
          f"(fingerprint {MORGAN_BITS} + descriptors {len(DESC_NAMES)})")
    print(f"  Train set ({len(train_idx):>4} rows): {ratio_str(y_train)}")
    print(f"  Test  set ({len(test_idx):>4} rows): {ratio_str(y_test)}")
    print(f"\n  Artifacts written to → {OUT_DIR}/")
    print(f"  Ready for model training.\n")


if __name__ == "__main__":
    main()
