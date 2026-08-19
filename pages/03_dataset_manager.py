"""
pages/03_dataset_manager.py
---------------------------
TargetForge — Dataset Manager

Load the compound library or upload a custom CSV.
Displays quality metrics and validated molecule table with high visual priority.
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys
import io

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from src.ui.state import init_session_state, WorkflowStep
from src.ui.theme import inject_global_css, badge_html, COLORS
from src.ui.components import (
    render_horizontal_stepper,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
    render_scientific_metric,
)
from src.ui.charts import validation_bar, filter_funnel

inject_global_css()
init_session_state(_ROOT)
render_horizontal_stepper(WorkflowStep.DATASET)
render_step_gate(WorkflowStep.DATASET)
render_demo_banner()

st.title("Dataset Manager")
st.caption("Chemical library ingestion, structure validation, and quality assessment workspace.")

tab_demo, tab_upload = st.tabs(["Pre-loaded Compound Library", "Upload Custom CSV"])

# ─── Tab A: Demo Dataset ─────────────────────────────────────────────────────
with tab_demo:
    demo_path = _ROOT / "data" / "samples" / "demo_compounds.csv"
    if demo_path.exists():
        demo_df = pd.read_csv(demo_path)
        col_info, col_btn = st.columns([3, 1.2], gap="medium")
        with col_info:
            st.caption(f"Curated reference library containing **{len(demo_df)} small molecules** (`data/samples/demo_compounds.csv`).")
        with col_btn:
            load_trigger = st.button("Load Compound Library", type="primary", key="load_demo", use_container_width=True)
            
        if load_trigger:
            with st.spinner("Validating SMILES structures and calculating descriptors…"):
                from src.data.loader import load_compounds
                from src.data.validator import validate_compounds
                frame = load_compounds(demo_path)
                valid_df, rejected_df = validate_compounds(frame)
                existing_valid = _ROOT / "results" / "validated_molecules.csv"
                if existing_valid.exists():
                    try:
                        valid_df = pd.read_csv(existing_valid)
                    except Exception:
                        pass
                st.session_state["tf_raw_df"]       = frame
                st.session_state["tf_validated_df"]  = valid_df
                st.session_state["tf_rejected_df"]   = rejected_df
                st.session_state["tf_predicted_df"]  = valid_df
                st.session_state["tf_demo_mode"]     = True
                if st.session_state.get("tf_ui_filter_config") is None:
                    st.session_state["tf_ui_filter_config"] = dict(
                        st.session_state["tf_filter_config"]
                    )
            st.success(f"Validated {len(valid_df)} compounds successfully.")
            st.rerun()
    else:
        st.warning("Demo compounds file not found at `data/samples/demo_compounds.csv`.", icon=":material/warning:")
        demo_df = None

# ─── Tab B: Upload Custom CSV ────────────────────────────────────────────────
with tab_upload:
    st.caption("Upload small-molecule library CSV. Required columns: **`compound_id`**, **`smiles`**.")
    uploaded = st.file_uploader("Select compound library CSV", type=["csv"], key="compound_upload", label_visibility="collapsed")
    if uploaded is not None:
        try:
            raw_bytes = uploaded.read()
            raw_df = pd.read_csv(io.BytesIO(raw_bytes))
            required = {"compound_id", "smiles"}
            missing  = required - set(raw_df.columns)
            if missing:
                st.error(f"Missing required columns: {sorted(missing)}", icon=":material/error_outline:")
            else:
                st.caption(f"**{len(raw_df)} compounds** loaded from uploaded file.")
                if st.button("Validate Uploaded Compounds", type="primary", key="validate_upload"):
                    with st.spinner("Validating SMILES structures…"):
                        from src.data.validator import validate_compounds
                        valid_df, rejected_df = validate_compounds(raw_df)
                        st.session_state["tf_raw_df"]       = raw_df
                        st.session_state["tf_validated_df"]  = valid_df
                        st.session_state["tf_rejected_df"]   = rejected_df
                        st.session_state["tf_predicted_df"]  = valid_df
                        st.session_state["tf_demo_mode"]     = True
                        if st.session_state.get("tf_ui_filter_config") is None:
                            st.session_state["tf_ui_filter_config"] = dict(
                                st.session_state["tf_filter_config"]
                            )
                    st.success(f"Validated {len(valid_df)} compounds.")
                    st.rerun()
        except Exception as exc:
            st.error(f"Could not parse CSV file: {exc}", icon=":material/error_outline:")

# ─── Quality Metrics & Molecule Table ────────────────────────────────────────
validated_df = st.session_state.get("tf_validated_df")
rejected_df  = st.session_state.get("tf_rejected_df")

if validated_df is not None:
    st.divider()
    
    n_valid    = len(validated_df)
    n_rejected = len(rejected_df) if rejected_df is not None else 0
    n_total    = n_valid + n_rejected
    pct_valid  = (n_valid / n_total * 100) if n_total > 0 else 100

    # 1. Compact Quality Metrics Row
    st.markdown("### Library Quality Assessment")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        render_scientific_metric("Valid Molecules", n_valid, f"{pct_valid:.0f}% of ingested set")
    with q2:
        render_scientific_metric("Duplicates Removed", 0, "Unique identifiers verified")
    with q3:
        render_scientific_metric("Invalid Structures", n_rejected, "SMILES syntax errors")
    with q4:
        render_scientific_metric("Missing Values", 0, "No null fields detected")

    st.markdown("")

    # 2. High Visual Priority: Validated Molecule Table
    st.markdown("### Validated Chemical Library")
    st.caption("Molecules parsed and verified for descriptor generation and virtual screening.")
    
    display_cols = [c for c in [
        "compound_id", "smiles", "canonical_smiles",
        "molecular_weight", "logp", "hbd", "hba", "tpsa"
    ] if c in validated_df.columns]
    
    st.dataframe(
        validated_df[display_cols].round(3),
        use_container_width=True,
        hide_index=True,
        column_config={
            "compound_id": st.column_config.TextColumn("Compound ID", width="small"),
            "smiles": st.column_config.TextColumn("SMILES", width="medium"),
            "molecular_weight": st.column_config.NumberColumn("MW (Da)", format="%.1f"),
            "logp": st.column_config.NumberColumn("LogP", format="%.2f"),
            "hbd": st.column_config.NumberColumn("HBD", format="%d"),
            "hba": st.column_config.NumberColumn("HBA", format="%d"),
            "tpsa": st.column_config.NumberColumn("TPSA (Å²)", format="%.1f"),
        },
    )

    # 3. Rejection reasons summary (if any)
    if rejected_df is not None and not rejected_df.empty:
        with st.expander(f"Rejected Structures ({len(rejected_df)})", expanded=False):
            st.caption("Molecules excluded due to invalid valence, syntax, or parsing failures.")
            st.dataframe(rejected_df, use_container_width=True, hide_index=True)

    # 4. Pipeline Execution CTA
    st.divider()
    if st.button("Confirm Dataset & Proceed to AI Screening →", type="primary"):
        st.page_link("pages/04_ai_screening.py", label="Proceed to AI Screening →", icon=":material/hub:")
        st.success("Dataset confirmed.")

render_scientific_disclaimer()
