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
    project_config: Optional[dict] = None,
    filter_config: Optional[dict] = None,
    weights: Optional[dict] = None,
) -> list[FrontendCandidate]:
    """Adapt backend DataFrame to list of FrontendCandidate dataclass objects."""
    if df is None or df.empty:
        return []

    # Handle flexible argument orders if caller passes (df, filter_config) vs (df, project_config, filter_config)
    if project_config and ("max_molecular_weight" in project_config or "max_logp" in project_config):
        cfg = project_config
        proj = filter_config or {}
    else:
        proj = project_config or {}
        cfg = filter_config or {
            "max_molecular_weight": 500.0,
            "max_logp":             5.0,
            "max_hbd":              5,
            "max_hba":              10,
            "max_tpsa":             140.0,
            "max_rotatable_bonds":  10,
        }

    receptor_id = str(proj.get("target", {}).get("structure_id", "6LU7")) if proj else "6LU7"

    candidates: list[FrontendCandidate] = []
    for idx, row in df.iterrows():
        props = MolecularProperties(
            mw              = _safe_float(row.get("molecular_weight")),
            logp            = _safe_float(row.get("logp")),
            hbd             = _safe_int(row.get("hbd")),
            hba             = _safe_int(row.get("hba")),
            tpsa            = _safe_float(row.get("tpsa")),
            rotatable_bonds = _safe_int(row.get("rotatable_bonds")),
        )

        filter_status = str(row.get("filter_status", "PASS")).upper()
        reasons_raw   = row.get("filter_reasons", "")
        reasons_list  = (
            [r.strip() for r in str(reasons_raw).split(";") if r.strip()]
            if reasons_raw and pd.notna(reasons_raw)
            else _derive_filter_reasons(row, cfg) if filter_status == "REJECTED" else []
        )

        filt = FilterResult(
            status          = filter_status,
            reasons         = reasons_list,
        )

        docking_raw = row.get("docking_score")
        dock = DockingResult(
            score_raw          = _safe_float(docking_raw) if pd.notna(docking_raw) else None,
            score_normalized   = _safe_float(row.get("docking_norm", 0.0)) if pd.notna(row.get("docking_norm")) else None,
            receptor_id        = receptor_id,
            docking_status     = str(row.get("docking_status", row.get("docking_source", "FALLBACK_DEMO"))),
        )

        candidate = FrontendCandidate(
            rank            = _safe_int(row.get("rank", idx + 1)),
            candidate_id    = str(row.get("compound_id", f"CMP-{idx+1:03d}")),
            smiles          = str(row.get("smiles", "")),
            activity_score  = _safe_float(row.get("activity_score", 0.0)),
            activity_norm   = _safe_float(row.get("activity_norm", row.get("activity_score", 0.0))),
            docking_norm    = _safe_float(row.get("docking_norm", 0.0)),
            property_score  = _safe_float(row.get("property_score", 1.0)),
            novelty_score   = _safe_float(row.get("novelty_score", 0.5)),
            final_score     = _safe_float(row.get("final_score", 0.0)),
            properties      = props,
            filter          = filt,
            docking         = dock,
            predicted_class = str(row.get("predicted_class", "active")),
            warnings        = list(_DEMO_WARNINGS),
        )
        candidates.append(candidate)

    return candidates


# ---------------------------------------------------------------------------
# Interactive filter re-computation (UI layer — mirrors backend logic)
# ---------------------------------------------------------------------------

def reapply_filters(validated_df: pd.DataFrame, ui_config: dict) -> pd.DataFrame:
    """UI-layer filter re-computation for interactive threshold sliders."""
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
    """Frontend-only what-if ranking using user-supplied weights."""
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


def compute_whatif_ranking(
    candidates: list[FrontendCandidate],
    whatif_weights: dict,
) -> list[FrontendCandidate]:
    """Alias for rerank_candidates."""
    return rerank_candidates(candidates, whatif_weights)


# ---------------------------------------------------------------------------
# Table & CSV formatting helpers
# ---------------------------------------------------------------------------

def build_ranking_table_df(candidates: list[FrontendCandidate]) -> pd.DataFrame:
    """Build a presentation DataFrame for the Final Ranking table."""
    records = []
    for c in candidates:
        records.append({
            "Rank":            c.rank,
            "Compound ID":     c.candidate_id,
            "Activity Score":  round(c.activity_score, 4),
            "Docking (kcal/mol)": round(c.docking.score_raw, 2) if c.docking.score_raw is not None else "N/A",
            "Property Score":  round(c.property_score, 2),
            "Novelty Score":   round(c.novelty_score, 2),
            "Composite Score": round(c.final_score, 4),
            "MW (Da)":         round(c.properties.mw, 1),
            "LogP":            round(c.properties.logp, 2),
            "Status":          c.filter.status,
        })
    return pd.DataFrame(records)


def build_ranking_csv(candidates: list[FrontendCandidate]) -> str:
    """Export the candidate list to a CSV string."""
    df = build_ranking_table_df(candidates)
    return df.to_csv(index=False)
