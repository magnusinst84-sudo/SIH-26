"""
validate_dataset.py
-------------------
Loads data/raw/mpro_labeled_smiles.csv and performs data-quality checks:
  1. SMILES parse rate
  2. Descriptor statistics
  3. Canonical SMILES deduplication
  4. Activity label sanity
  5. MW distribution by bin (Active/Inactive) -- saved to results/data_quality_report.txt
"""

import os
import sys
import io
import warnings
import pandas as pd
import numpy as np

# Force stdout to UTF-8 on Windows so Unicode chars don't crash cp1252 terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Suppress RDKit stderr noise
try:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Descriptors, rdMolDescriptors
    RDLogger.DisableLog("rdApp.*")
except ImportError:
    print("ERROR: RDKit is not installed. Install it with:\n  pip install rdkit")
    sys.exit(1)

INPUT_CSV   = "data/raw/mpro_labeled_smiles.csv"
REPORT_PATH = "results/data_quality_report.txt"

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _banner(text: str, char="=", width=70) -> str:
    line = char * width
    return f"\n{line}\n  {text}\n{line}"


def _stat_block(series: pd.Series, name: str) -> str:
    return (
        f"  {name:<28}  mean={series.mean():.2f}  median={series.median():.2f}"
        f"  min={series.min():.2f}  max={series.max():.2f}"
    )


def _stop_banner(reason: str):
    msg = (
        "\n" + "!" * 70 + "\n"
        "  *** STOP ***\n"
        + "!" * 70
        + f"\n\n  REASON: {reason}\n\n" + "!" * 70
    )
    print(msg)


def parse_smiles(smiles: str):
    """Returns RDKit Mol or None."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol  # None if invalid
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    lines = []  # collect everything for the report too

    def log(text=""):
        print(text)
        lines.append(text)

    # ── Load ──────────────────────────────────────────────────────────────────
    log(_banner("LOADING DATASET"))
    if not os.path.exists(INPUT_CSV):
        log(f"ERROR: {INPUT_CSV} not found. Run prepare_dataset.py first.")
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV)
    total_rows = len(df)
    log(f"  Loaded {total_rows} rows from {INPUT_CSV}")
    log(f"  Columns: {list(df.columns)}")
    log(f"  Labels present: {df['activity_label'].value_counts().to_dict()}")

    # ── 1. SMILES Parsing ────────────────────────────────────────────────────
    log(_banner("1. SMILES PARSE RATE"))

    df["mol"] = df["smiles"].apply(parse_smiles)
    parse_ok   = df["mol"].notna()
    parse_fail = ~parse_ok

    n_ok   = parse_ok.sum()
    n_fail = parse_fail.sum()
    fail_rate = n_fail / total_rows * 100

    log(f"  Total rows         : {total_rows}")
    log(f"  Parse successes    : {n_ok}")
    log(f"  Parse failures     : {n_fail}  ({fail_rate:.2f}%)")

    if n_fail > 0:
        log(f"\n  First {min(5, n_fail)} failures:")
        for _, row in df[parse_fail].head(5).iterrows():
            log(f"    compound_id={row['compound_id']}  smiles={row['smiles']}")

    if fail_rate > 5.0:
        _stop_banner(
            f"{fail_rate:.1f}% of SMILES failed to parse — exceeds 5% threshold.\n"
            "  The dataset may contain corrupt or non-standard SMILES.\n"
            "  Do NOT proceed to model training without fixing these."
        )

    # ── 2. Descriptor Statistics ─────────────────────────────────────────────
    log(_banner("2. DESCRIPTOR STATISTICS (valid mols only)"))

    df_ok = df[parse_ok].copy()

    df_ok["MW"]        = df_ok["mol"].apply(Descriptors.MolWt)
    df_ok["logP"]      = df_ok["mol"].apply(Descriptors.MolLogP)
    df_ok["TPSA"]      = df_ok["mol"].apply(Descriptors.TPSA)
    df_ok["RotBonds"]  = df_ok["mol"].apply(rdMolDescriptors.CalcNumRotatableBonds)
    df_ok["HBD"]       = df_ok["mol"].apply(rdMolDescriptors.CalcNumHBD)
    df_ok["HBA"]       = df_ok["mol"].apply(rdMolDescriptors.CalcNumHBA)

    for col, name in [
        ("MW",       "Mol Weight (Da)"),
        ("logP",     "LogP"),
        ("TPSA",     "TPSA (Å²)"),
        ("RotBonds", "Rotatable Bonds"),
        ("HBD",      "H-Bond Donors"),
        ("HBA",      "H-Bond Acceptors"),
    ]:
        log(_stat_block(df_ok[col], name))

    # ── 3. Canonical SMILES Deduplication ────────────────────────────────────
    log(_banner("3. CANONICAL SMILES DEDUPLICATION"))

    df_ok["canonical_smiles"] = df_ok["mol"].apply(
        lambda m: Chem.MolToSmiles(m, canonical=True) if m else None
    )

    n_unique = df_ok["canonical_smiles"].nunique()
    log(f"  Total valid rows       : {n_ok}")
    log(f"  Unique canonical SMILES: {n_unique}")
    log(f"  Duplicate structures   : {n_ok - n_unique}")

    # Find CIDs sharing the same canonical SMILES
    dup_groups = (
        df_ok.groupby("canonical_smiles")["compound_id"]
        .filter(lambda g: len(g) > 1)
    )
    if len(dup_groups) > 0:
        dup_detail = (
            df_ok[df_ok["compound_id"].isin(dup_groups)]
            .groupby("canonical_smiles")["compound_id"]
            .apply(list)
        )
        log(f"\n  CIDs sharing identical canonical SMILES (first 10 groups):")
        for smi, cids in list(dup_detail.items())[:10]:
            log(f"    SMILES={smi[:60]}...  CIDs={cids}")
    else:
        log("  No CIDs share identical canonical SMILES — all structures are unique.")

    # ── 4. Activity Label Sanity ──────────────────────────────────────────────
    log(_banner("4. ACTIVITY LABEL SANITY"))

    act_col = "activity_value_um"
    has_values = df_ok[act_col].notna()
    n_with_values = has_values.sum()

    log(f"  Rows with activity_value_um populated: {n_with_values} / {n_ok}")

    if n_with_values > 0:
        by_label = df_ok[has_values].groupby("activity_label")[act_col]
        medians  = by_label.median()
        log(f"  Median Activity Value [uM]:")
        for label, med in medians.items():
            log(f"    {label:<12}: {med:.4f} uM")

        if "active" in medians and "inactive" in medians:
            if medians["inactive"] < medians["active"]:
                warning_msg = (
                    "INVERTED ACTIVITY: Inactives have a LOWER (more potent) median\n"
                    "  Activity Value than Actives. This suggests the labels may be\n"
                    "  swapped, or the activity column is not IC50/EC50 (lower=better)."
                )
                log(f"\n  ⚠  WARNING: {warning_msg}")
                _stop_banner(warning_msg)
            else:
                log("  ✓  Activity direction looks correct (Actives ≤ Inactives by median).")
    else:
        log("  activity_value_um is empty for all rows — skipping median comparison.")
        log("  NOTE: The source assay (PubChem AID 1706) uses qualitative Active/Inactive")
        log("        labels; quantitative IC50s are not available for most compounds.")

    # ── 5. MW Distribution by Bin ─────────────────────────────────────────────
    log(_banner("5. MW DISTRIBUTION BY 100 Da BIN"))

    bin_edges = list(range(0, int(df_ok["MW"].max()) + 100, 100))
    df_ok["mw_bin"] = pd.cut(df_ok["MW"], bins=bin_edges, right=False)

    dist = (
        df_ok.groupby(["mw_bin", "activity_label"], observed=True)
        .size()
        .unstack(fill_value=0)
    )

    # Ensure both columns exist
    for col in ["active", "inactive"]:
        if col not in dist.columns:
            dist[col] = 0
    dist = dist[["active", "inactive"]]
    dist["total"] = dist["active"] + dist["inactive"]
    dist = dist[dist["total"] > 0]

    # Header
    header = f"\n  {'MW Bin (Da)':<20} {'Active':>8} {'Inactive':>10} {'Total':>8}  Bar"
    log(header)
    log("  " + "-" * 60)
    for mw_bin, row in dist.iterrows():
        bar = "#" * min(int(row["total"] / max(dist["total"].max(), 1) * 30), 30)
        log(f"  {str(mw_bin):<20} {row['active']:>8} {row['inactive']:>10} {row['total']:>8}  {bar}")

    # ── Write report ──────────────────────────────────────────────────────────
    os.makedirs("results", exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n  Report saved → {REPORT_PATH}")


if __name__ == "__main__":
    main()
