"""
src/ui/state.py
---------------
Session-state schema, enumerations, and workflow-step management.

All session keys are prefixed with "tf_" to avoid collisions.
Invariants enforced:
  - tf_ranked_df   is written once and never mutated by UI code.
  - tf_weights     is written once from configs/project.yaml.
  - tf_filter_config is written once from configs/filters.yaml.
  - What-if data goes to tf_whatif_weights / tf_whatif_ranked only.

Owned by: M4 (Frontend/UI Lead)
"""
from __future__ import annotations

from enum import IntEnum, Enum
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
import yaml


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class WorkflowStep(IntEnum):
    TARGET    = 1
    DATASET   = 2
    SCREENING = 3
    DESIGN    = 4
    DOCKING   = 5
    RANKING   = 6
    REPORTS   = 7


class StepStatus(str, Enum):
    LOCKED    = "locked"
    CURRENT   = "current"
    COMPLETED = "completed"
    FAILED    = "failed"


# ---------------------------------------------------------------------------
# Workflow metadata
# ---------------------------------------------------------------------------

PREREQUISITES: dict[WorkflowStep, Optional[str]] = {
    WorkflowStep.TARGET:    None,
    WorkflowStep.DATASET:   "tf_target",
    WorkflowStep.SCREENING: "tf_validated_df",
    WorkflowStep.DESIGN:    "tf_validated_df",
    WorkflowStep.DOCKING:   "tf_filtered_df",
    WorkflowStep.RANKING:   "tf_docked_df",
    WorkflowStep.REPORTS:   "tf_ranked_df",
}

# Key whose non-None presence signals the step is complete
COMPLETION_KEYS: dict[WorkflowStep, str] = {
    WorkflowStep.TARGET:    "tf_target",
    WorkflowStep.DATASET:   "tf_validated_df",
    WorkflowStep.SCREENING: "tf_predicted_df",
    WorkflowStep.DESIGN:    "tf_filtered_df",
    WorkflowStep.DOCKING:   "tf_docked_df",
    WorkflowStep.RANKING:   "tf_ranked_df",
    WorkflowStep.REPORTS:   "tf_ranked_df",
}

STEP_LABELS: dict[WorkflowStep, tuple[str, str]] = {
    WorkflowStep.TARGET:    ("", "Target Explorer"),
    WorkflowStep.DATASET:   ("", "Dataset Manager"),
    WorkflowStep.SCREENING: ("", "AI Screening"),
    WorkflowStep.DESIGN:    ("", "Candidate Design"),
    WorkflowStep.DOCKING:   ("", "Docking Analysis"),
    WorkflowStep.RANKING:   ("", "Final Ranking"),
    WorkflowStep.REPORTS:   ("", "Reports"),
}

PAGE_PATHS: dict[WorkflowStep, str] = {
    WorkflowStep.TARGET:    "pages/02_target_explorer.py",
    WorkflowStep.DATASET:   "pages/03_dataset_manager.py",
    WorkflowStep.SCREENING: "pages/04_ai_screening.py",
    WorkflowStep.DESIGN:    "pages/05_candidate_design.py",
    WorkflowStep.DOCKING:   "pages/06_docking_analysis.py",
    WorkflowStep.RANKING:   "pages/07_final_ranking.py",
    WorkflowStep.REPORTS:   "pages/08_reports.py",
}


# ---------------------------------------------------------------------------
# Config loader (reads project.yaml / filters.yaml — backend configs, read-only)
# ---------------------------------------------------------------------------

def _load_configs(root: Path) -> tuple[dict, dict]:
    """Read project.yaml and filters.yaml. Returns (project_cfg, filters_cfg)."""
    project_path = root / "configs" / "project.yaml"
    filters_path = root / "configs" / "filters.yaml"
    project: dict = {}
    filters_cfg: dict = {}
    try:
        with open(project_path, encoding="utf-8") as fh:
            project = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        pass
    try:
        with open(filters_path, encoding="utf-8") as fh:
            filters_cfg = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        pass
    return project, filters_cfg


# ---------------------------------------------------------------------------
# Session-state initialiser
# ---------------------------------------------------------------------------

def init_session_state(root: Path) -> None:
    """
    Idempotent session-state initialiser.  Safe to call at the top of every
    page module.  Only fills keys that are not already set.
    """
    if "tf_root" not in st.session_state:
        st.session_state["tf_root"] = root

    # --- Load backend configs (read-only references) once per session ---
    if "tf_target" not in st.session_state:
        project, filters_cfg = _load_configs(root)
        target_raw = project.get("target", {})
        ranking_raw = project.get("ranking", {})
        model_raw = project.get("model", {})

        st.session_state["tf_target"] = {
            "name":         target_raw.get("name",         "SARS-CoV-2 main protease"),
            "aliases":      target_raw.get("aliases",      ["Mpro", "3CLpro"]),
            "structure_id": target_raw.get("structure_id", "6LU7"),
            "disease":      project.get("disease",         "COVID-19"),
            "application":  project.get("application",     "mpro_screening"),
            "project_name": project.get("project_name",    "TargetForge"),
            "model_type":   model_raw.get("type",          "demo_activity_model"),
            "model_version": model_raw.get("version",      "demo_v1"),
        }
        # INVARIANT: tf_weights — written once from config, never overwritten by UI
        st.session_state["tf_weights"] = {
            "activity_weight": ranking_raw.get("activity_weight", 0.40),
            "docking_weight":  ranking_raw.get("docking_weight",  0.30),
            "property_weight": ranking_raw.get("property_weight", 0.20),
            "novelty_weight":  ranking_raw.get("novelty_weight",  0.10),
        }
        # INVARIANT: tf_filter_config — written once from config, never overwritten by UI
        st.session_state["tf_filter_config"] = {
            "max_molecular_weight": filters_cfg.get("max_molecular_weight", 500),
            "max_logp":             filters_cfg.get("max_logp",             5.0),
            "max_hbd":              filters_cfg.get("max_hbd",              5),
            "max_hba":              filters_cfg.get("max_hba",              10),
            "max_tpsa":             filters_cfg.get("max_tpsa",             140),
            "max_rotatable_bonds":  10,   # UI-only default — not in filters.yaml
        }

    # --- Remaining defaults (only set if missing) ---
    _defaults: dict = {
        "tf_demo_mode":        True,
        "tf_pipeline_ran":     False,
        "tf_step_status":      {s: StepStatus.LOCKED for s in WorkflowStep},
        "tf_raw_df":           None,
        "tf_validated_df":     None,
        "tf_rejected_df":      None,
        "tf_predicted_df":     None,
        "tf_model_meta":       None,
        "tf_ui_filter_config": None,
        "tf_filtered_df":      None,
        "tf_docked_df":        None,
        "tf_docking_meta":     None,
        "tf_ranked_df":        None,   # INVARIANT: read-only after first write
        "tf_whatif_weights":   None,
        "tf_whatif_ranked":    None,
        "tf_candidates":       None,
    }
    for key, value in _defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --- Pre-load results that already exist on disk ---
    if not st.session_state["tf_pipeline_ran"]:
        _try_preload_results(root)

    # --- Refresh step statuses from current data presence ---
    _refresh_step_statuses()


def _try_preload_results(root: Path) -> None:
    """
    If results CSVs already exist on disk (from a previous pipeline run),
    pre-load them into session state so the app is immediately usable.
    Mirrors the original app.py fallback branch.
    """
    ranking_path  = root / "results" / "final_ranking.csv"
    valid_path    = root / "results" / "validated_molecules.csv"
    rejected_path = root / "results" / "rejected_molecules.csv"

    if ranking_path.exists() and st.session_state.get("tf_ranked_df") is None:
        try:
            ranked_df = pd.read_csv(ranking_path)
            if not ranked_df.empty:
                # INVARIANT: tf_ranked_df written once
                st.session_state["tf_ranked_df"] = ranked_df
                st.session_state["tf_docked_df"] = ranked_df
                st.session_state["tf_pipeline_ran"] = True
                st.session_state["tf_demo_mode"]    = True
                # Build FrontendCandidate list via adapter
                from src.ui.adapter import adapt_ranked_df
                project_cfg = {
                    "target": {
                        "structure_id": st.session_state["tf_target"].get(
                            "structure_id", "6LU7"
                        )
                    }
                }
                st.session_state["tf_candidates"] = adapt_ranked_df(
                    ranked_df, project_cfg, st.session_state["tf_filter_config"]
                )
                # Also initialise ui_filter_config from backend defaults
                if st.session_state.get("tf_ui_filter_config") is None:
                    st.session_state["tf_ui_filter_config"] = dict(
                        st.session_state["tf_filter_config"]
                    )
        except Exception:
            pass

    if valid_path.exists() and st.session_state.get("tf_validated_df") is None:
        try:
            validated = pd.read_csv(valid_path)
            if not validated.empty:
                st.session_state["tf_validated_df"] = validated
                st.session_state["tf_predicted_df"] = validated

                # Build filtered_df from loaded ranked data (all are PASS in demo)
                if st.session_state.get("tf_ranked_df") is not None:
                    ranked_df = st.session_state["tf_ranked_df"]
                    if "filter_status" in ranked_df.columns:
                        st.session_state["tf_filtered_df"] = ranked_df[
                            ranked_df["filter_status"] == "PASS"
                        ].copy()
        except Exception:
            pass

    if rejected_path.exists() and st.session_state.get("tf_rejected_df") is None:
        try:
            rejected = pd.read_csv(rejected_path)
            st.session_state["tf_rejected_df"] = rejected
        except Exception:
            pass


def _refresh_step_statuses() -> None:
    """Recompute tf_step_status based on data presence in session state."""
    statuses: dict[WorkflowStep, StepStatus] = {}
    for step in WorkflowStep:
        prereq_key = PREREQUISITES[step]
        prereq_met = (
            prereq_key is None
            or st.session_state.get(prereq_key) is not None
        )
        if not prereq_met:
            statuses[step] = StepStatus.LOCKED
        else:
            completion_key = COMPLETION_KEYS[step]
            if st.session_state.get(completion_key) is not None:
                statuses[step] = StepStatus.COMPLETED
            else:
                statuses[step] = StepStatus.CURRENT
    st.session_state["tf_step_status"] = statuses


# ---------------------------------------------------------------------------
# Public accessors
# ---------------------------------------------------------------------------

def is_step_accessible(step: WorkflowStep) -> bool:
    """Return True if the step's prerequisite is satisfied."""
    prereq_key = PREREQUISITES[step]
    if prereq_key is None:
        return True
    return st.session_state.get(prereq_key) is not None


def get_step_status(step: WorkflowStep) -> StepStatus:
    """Return the current display status for a workflow step."""
    return st.session_state.get("tf_step_status", {}).get(step, StepStatus.LOCKED)


def populate_from_pipeline(
    root: Path,
    ranked_df: pd.DataFrame,
) -> None:
    """
    Called from the Home page after run_demo() returns.
    Populates ALL tf_* keys from the pipeline output.
    INVARIANT: tf_ranked_df and tf_weights are set here and never
               overwritten by UI code afterwards.
    """
    from src.ui.adapter import adapt_ranked_df

    results_dir = root / "results"

    # INVARIANT: tf_ranked_df — written once here
    st.session_state["tf_ranked_df"]  = ranked_df
    st.session_state["tf_docked_df"]  = ranked_df
    st.session_state["tf_pipeline_ran"] = True
    st.session_state["tf_demo_mode"]    = True

    # Load intermediate CSVs written by run_demo() as side effects
    valid_path    = results_dir / "validated_molecules.csv"
    rejected_path = results_dir / "rejected_molecules.csv"
    try:
        if valid_path.exists():
            validated = pd.read_csv(valid_path)
            st.session_state["tf_validated_df"] = validated
            st.session_state["tf_predicted_df"] = validated
    except Exception:
        pass
    try:
        if rejected_path.exists():
            st.session_state["tf_rejected_df"] = pd.read_csv(rejected_path)
    except Exception:
        pass

    # Initialise UI filter config from backend defaults (if not already set)
    if st.session_state.get("tf_ui_filter_config") is None:
        st.session_state["tf_ui_filter_config"] = dict(
            st.session_state["tf_filter_config"]
        )

    # Build filtered_df from ranked data (all ranked are PASS)
    if "filter_status" in ranked_df.columns:
        st.session_state["tf_filtered_df"] = ranked_df[
            ranked_df["filter_status"] == "PASS"
        ].copy()

    # Adapt to FrontendCandidate list
    project_cfg = {
        "target": {
            "structure_id": st.session_state["tf_target"].get("structure_id", "6LU7")
        }
    }
    st.session_state["tf_candidates"] = adapt_ranked_df(
        ranked_df, project_cfg, st.session_state["tf_filter_config"]
    )

    st.session_state["tf_model_meta"] = {
        "model_version": st.session_state["tf_target"].get("model_version", "demo_v1"),
        "model_type":    st.session_state["tf_target"].get("model_type",    "demo_activity_model"),
    }
    st.session_state["tf_docking_meta"] = {
        "tool":        "fallback",
        "receptor_id": st.session_state["tf_target"].get("structure_id", "6LU7"),
        "is_fallback": True,
    }

    _refresh_step_statuses()
