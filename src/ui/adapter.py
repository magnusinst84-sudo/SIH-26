"""
src/ui/adapter.py
-----------------
Adapter / normalisation layer between the 24-column backend DataFrame
and the FrontendCandidate schema.

INVARIANTS enforced here:
  - adapt_ranked_df() READS the DataFrame; it NEVER writes back.
  - final_score and rank on FrontendCandidate are set exactly once,
    from the corresponding backend columns.
  - reapply_filters() mirrors the backend filter logic for interactive
    slider support.  It does NOT call src.molecular_ai.filters.apply_filters().
  - rerank_candidates() creates deep-copied objects; originals are untouched.

Owned by: M4 (Frontend/UI Lead)
"""
from __future__ import annotations

import copy
from typing import Any, Optional

import pandas as pd

from src.ui.schema import (
    DockingResult,
    FilterResult,
    FrontendCandidate,
    MolecularProperties,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_DEMO_WARNINGS = [
    "activity_score: deterministic demo value derived from SHA-256(compound_id). Not a real ML prediction.",
    "docking_score: FALLBACK_DEMO value — no real docking simulation was performed.",
    "novelty_score: hardcoded to 0.5 for all demo candidates.",
]


def _derive_filter_reasons(row: "pd.Series[Any]", config: dict) -> list[str]:
    """
    Derive human-readable filter failure reasons from descriptor values
    and threshold config.  Pure UI-layer logic — does not call backend.
    """
    reasons: list[str] = []
    mw  = row.get("molecular_weight", 0.0)
    lp  = row.get("logp",             0.0)
    hbd = row.get("hbd",              0)
    hba = row.get("hba",              0)
    tps = row.get("tpsa",             0.0)
    rb  = row.get("rotatable_bonds",  0)

    if mw  > config.get("max_molecular_weight", 500):
        reasons.append(f"MW {mw:.1f} > {config['max_molecular_weight']} Da")
    if lp  > config.get("max_logp",             5.0):
        reasons.append(f"LogP {lp:.2f} > {config['max_logp']}")
    if hbd > config.get("max_hbd",              5):
        reasons.append(f"HBD {hbd} > {config['max_hbd']}")
    if hba > config.get("max_hba",              10):
        reasons.append(f"HBA {hba} > {config['max_hba']}")
    if tps > config.get("max_tpsa",             140):
        reasons.append(f"TPSA {tps:.1f} > {config['max_tpsa']} Å²")
    if rb  > config.get("max_rotatable_bonds",  10):
        reasons.append(f"Rotatable bonds {rb} > {config['max_rotatable_bonds']} (UI threshold)")
    return reasons


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    try:
        return bool(value)
    except Exception:
        return default


# ---------------------------------------------------------------------------
# Primary adapter: 24-column DataFrame → list[FrontendCandidate]
# ---------------------------------------------------------------------------

def adapt_ranked_df(
    df: pd.DataFrame,
    project_config: dict,
    filter_config: dict,
) -> list[FrontendCandidate]:
    """
    Map the 24-column backend ranking DataFrame to a list of FrontendCandidate
    objects.

    Parameters
    ----------
    df             : The DataFrame returned by run_demo() or loaded from
                     results/final_ranking.csv  (READ-ONLY; never mutated).
    project_config : dict with at least {"target": {"structure_id": "6LU7"}}
    filter_config  : dict with max_molecular_weight, max_logp, etc.

    Returns a list ordered by rank (ascending).
    """
    receptor_id = (
        project_config.get("target", {}).get("structure_id")
        or "6LU7"
    )
    candidates: list[FrontendCandidate] = []

    for _, row in df.iterrows():
        is_demo = _safe_bool(row.get("is_fallback"), True)
        fs      = row.get("filter_status", "UNKNOWN")
        reasons = _derive_filter_reasons(row, filter_config) if fs == "REJECTED" else []

        cand = FrontendCandidate(
            # Identity
            candidate_id  = str(row.get("compound_id", "")),
            smiles        = str(row.get("smiles",       "")),
            source        = str(row.get("activity_label", "demo")),
            parent_id     = None,

            # ML prediction (BACKEND — read-only)
            activity_score  = _safe_float(row.get("activity_score")),
            model_version   = str(row.get("model_version", "demo_v1")),
            predicted_class = str(row.get("predicted_class", "unknown")),

            # Molecular properties (BACKEND — read-only)
            properties = MolecularProperties(
                mw               = _safe_float(row.get("molecular_weight")),
                logp             = _safe_float(row.get("logp")),
                hbd              = _safe_int(row.get("hbd")),
                hba              = _safe_int(row.get("hba")),
                tpsa             = _safe_float(row.get("tpsa")),
                rotatable_bonds  = _safe_int(row.get("rotatable_bonds")),
            ),

            # Filter (BACKEND status; reasons derived in UI layer)
            property_score = _safe_float(row.get("property_score")),
            filter = FilterResult(
                status  = str(fs),
                reasons = reasons,
            ),

            # Docking (BACKEND — read-only)
            docking = DockingResult(
                score_raw          = _safe_float(row.get("docking_score"))
                                     if pd.notna(row.get("docking_score")) else None,
                score_normalized   = _safe_float(row.get("docking_norm"))
                                     if pd.notna(row.get("docking_norm")) else None,
                pose_file          = None,           # not in demo backend
                receptor_id        = receptor_id,
                interaction_residues = [],           # not in demo backend
                docking_status     = str(row.get("docking_status", "UNKNOWN")),
            ),

            # Ranking scores (BACKEND — read-only)
            novelty_score = _safe_float(row.get("novelty_score"), 0.5),
            final_score   = _safe_float(row.get("final_score")),   # INVARIANT
            rank          = _safe_int(row.get("rank")),            # INVARIANT
            status        = str(row.get("status", "priority computational candidate")),

            # Normalised components (stored for what-if only)
            activity_norm = _safe_float(row.get("activity_norm")),
            docking_norm  = _safe_float(row.get("docking_norm")),

            # UI metadata
            is_demo  = is_demo,
            warnings = _DEMO_WARNINGS if is_demo else [],
        )
        candidates.append(cand)

    return sorted(candidates, key=lambda c: c.rank)


# ---------------------------------------------------------------------------
# Adapter for validated (non-ranked) compounds
# ---------------------------------------------------------------------------

def adapt_validated_df(df: pd.DataFrame) -> list[dict]:
    """
    Return a simplified list of dicts from the validated_molecules DataFrame.
    Used for display on Dataset Manager and Candidate Design pages.
    """
    result = []
    for _, row in df.iterrows():
        result.append({
            "compound_id":      str(row.get("compound_id", "")),
            "smiles":           str(row.get("smiles",       "")),
            "canonical_smiles": str(row.get("canonical_smiles", row.get("smiles", ""))),
            "mw":               _safe_float(row.get("molecular_weight")),
            "logp":             _safe_float(row.get("logp")),
            "hbd":              _safe_int(row.get("hbd")),
            "hba":              _safe_int(row.get("hba")),
            "tpsa":             _safe_float(row.get("tpsa")),
            "rotatable_bonds":  _safe_int(row.get("rotatable_bonds")),
            "activity_label":   str(row.get("activity_label", "demo")),
        })
    return result


# ---------------------------------------------------------------------------
# Interactive filter re-computation (UI layer — mirrors backend logic)
# ---------------------------------------------------------------------------

def reapply_filters(validated_df: pd.DataFrame, ui_config: dict) -> pd.DataFrame:
    """
    UI-layer filter re-computation for interactive threshold sliders.

    Mirrors the logic of src.molecular_ai.filters.apply_filters() but uses
    ui_config from the slider state instead of the static filters.yaml config.
    Does NOT call apply_filters() — avoids importing M6 code from UI.

    Parameters
    ----------
    validated_df : pd.DataFrame with descriptor columns already present.
    ui_config    : dict with max_molecular_weight, max_logp, max_hbd,
                   max_hba, max_tpsa, max_rotatable_bonds.

    Returns a new DataFrame (copy) with updated filter_status, property_score,
    and filter_reasons columns.  Original DataFrame is NOT mutated.
    """
    out = validated_df.copy()

    has_rb = "rotatable_bonds" in out.columns

    mw_ok  = out["molecular_weight"] <= ui_config.get("max_molecular_weight", 500)
    lp_ok  = out["logp"]             <= ui_config.get("max_logp",             5.0)
    hbd_ok = out["hbd"]              <= ui_config.get("max_hbd",              5)
    hba_ok = out["hba"]              <= ui_config.get("max_hba",              10)
    tp_ok  = out["tpsa"]             <= ui_config.get("max_tpsa",             140)
    rb_ok  = (
        out["rotatable_bonds"]       <= ui_config.get("max_rotatable_bonds",  10)
        if has_rb
        else pd.Series(True, index=out.index)
    )

    passed = mw_ok & lp_ok & hbd_ok & hba_ok & tp_ok & rb_ok
    out["filter_status"]  = passed.map({True: "PASS", False: "REJECTED"})
    out["property_score"] = passed.astype(float)
    out["filter_reasons"] = out.apply(
        lambda row: "; ".join(_derive_filter_reasons(row, ui_config))
        if row["filter_status"] == "REJECTED" else "",
        axis=1,
    )
    return out


# ---------------------------------------------------------------------------
# What-if re-ranking (UI layer — never modifies backend candidates)
# ---------------------------------------------------------------------------

def rerank_candidates(
    candidates: list[FrontendCandidate],
    whatif_weights: dict,
) -> list[FrontendCandidate]:
    """
    Frontend-only what-if ranking using user-supplied weights.

    Creates DEEP COPIES of each FrontendCandidate so that the originals
    are NEVER mutated.  Sets .whatif_score and .whatif_rank on the copies.
    The copies' .final_score and .rank remain the original backend values.

    Parameters
    ----------
    candidates    : The canonical list from tf_candidates (read-only).
    whatif_weights: dict with activity_weight, docking_weight,
                    property_weight, novelty_weight.

    Returns a new list of deep-copied candidates sorted by whatif_score.
    """
    aw = float(whatif_weights.get("activity_weight",  0.40))
    dw = float(whatif_weights.get("docking_weight",   0.30))
    pw = float(whatif_weights.get("property_weight",  0.20))
    nw = float(whatif_weights.get("novelty_weight",   0.10))

    result: list[FrontendCandidate] = []
    for original in candidates:
        wc = copy.deepcopy(original)
        wc.whatif_score = (
            aw * wc.activity_norm
            + dw * wc.docking_norm
            + pw * wc.property_score
            + nw * wc.novelty_score
        )
        result.append(wc)

    result.sort(key=lambda c: c.whatif_score or 0.0, reverse=True)
    for i, wc in enumerate(result):
        wc.whatif_rank = i + 1
    return result
