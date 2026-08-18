"""
pages/03_dataset_manager.py
---------------------------
TargetForge — Dataset Manager

Load the demo compound library or upload a custom CSV.
Displays validation results and funnel statistics.
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
from src.ui.theme import inject_global_css
from src.ui.components import (
    render_sidebar_progress,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
)
from src.ui.charts import validation_bar, filter_funnel

inject_global_css()
init_session_state(_ROOT)
render_sidebar_progress()
render_step_gate(WorkflowStep.DATASET)
render_demo_banner()

st.title("📂 Dataset Manager")
st.caption("Load a compound library for screening.")

tab_demo, tab_upload = st.tabs(["🧪 Demo Dataset", "📤 Upload Custom CSV"])

# ─── Tab A: Demo Dataset ─────────────────────────────────────────────────────
with tab_demo:
    demo_path = _ROOT / "data" / "samples" / "demo_compounds.csv"
    if demo_path.exists():
        demo_df = pd.read_csv(demo_path)
        st.markdown(f"**{len(demo_df)} demo compounds** from `data/samples/demo_compounds.csv`")
        st.dataframe(demo_df, use_container_width=True, hide_index=True)
    else:
        st.warning(
            "Demo compounds file not found. Run `python scripts/prepare_demo.py` first.",
            icon="⚠️",
        )
        demo_df = None

    if st.button("Load Demo Dataset", type="primary", key="load_demo"):
        if demo_df is not None:
            with st.spinner("Validating demo compounds…"):
                from src.data.loader import load_compounds
                from src.data.validator import validate_compounds
                frame = load_compounds(demo_path)
                valid_df, rejected_df = validate_compounds(frame)
                # Attach descriptor columns if available from prior run
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
            st.success(f"✅ Loaded {len(valid_df)} valid compounds, {len(rejected_df)} rejected.")
            st.rerun()

# ─── Tab B: Upload Custom CSV ────────────────────────────────────────────────
with tab_upload:
    st.info(
        "Upload a CSV with at minimum these columns: **`compound_id`**, **`smiles`**. "
        "An optional `activity_label` column is also accepted.",
        icon="ℹ️",
    )
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"], key="compound_upload")
    if uploaded is not None:
        try:
            raw_bytes = uploaded.read()
            raw_df = pd.read_csv(io.BytesIO(raw_bytes))
            required = {"compound_id", "smiles"}
            missing  = required - set(raw_df.columns)
            if missing:
                st.error(f"Missing required columns: {sorted(missing)}", icon="❌")
            else:
                st.markdown(f"**{len(raw_df)} compounds loaded from upload.**")
                st.dataframe(raw_df.head(10), use_container_width=True, hide_index=True)
                if st.button("Validate Uploaded Compounds", type="primary", key="validate_upload"):
                    with st.spinner("Validating SMILES…"):
                        from src.data.validator import validate_compounds
                        valid_df, rejected_df = validate_compounds(raw_df)
                        st.session_state["tf_raw_df"]       = raw_df
                        st.session_state["tf_validated_df"]  = valid_df
                        st.session_state["tf_rejected_df"]   = rejected_df
                        st.session_state["tf_predicted_df"]  = valid_df
                        st.session_state["tf_demo_mode"]     = True  # scores still demo
                        if st.session_state.get("tf_ui_filter_config") is None:
                            st.session_state["tf_ui_filter_config"] = dict(
                                st.session_state["tf_filter_config"]
                            )
                    st.success(
                        f"✅ Validated: {len(valid_df)} valid / {len(rejected_df)} rejected."
                    )
                    st.rerun()
        except Exception as exc:
            st.error(f"Could not read file: {exc}", icon="❌")

# ─── Validation Results ──────────────────────────────────────────────────────
validated_df = st.session_state.get("tf_validated_df")
rejected_df  = st.session_state.get("tf_rejected_df")

if validated_df is not None:
    st.divider()
    st.markdown("### Validation Results")

    n_valid    = len(validated_df)
    n_rejected = len(rejected_df) if rejected_df is not None else 0
    n_total    = n_valid + n_rejected

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Loaded",  n_total)
    m2.metric("✓ Valid",        n_valid)
    m3.metric("✗ Rejected",     n_rejected)

    col_chart, col_funnel = st.columns(2)
    with col_chart:
        st.plotly_chart(validation_bar(n_valid, n_rejected), use_container_width=True)
    with col_funnel:
        ranked_df = st.session_state.get("tf_ranked_df")
        n_docked = len(ranked_df) if ranked_df is not None else 0
        st.plotly_chart(
            filter_funnel(n_total, n_valid, n_valid),
            use_container_width=True,
        )

    # Valid compounds table
    st.markdown("#### ✓ Valid Compounds")
    display_cols = [c for c in [
        "compound_id", "smiles", "canonical_smiles",
        "molecular_weight", "logp", "hbd", "hba", "tpsa"
    ] if c in validated_df.columns]
    st.dataframe(
        validated_df[display_cols].round(3),
        use_container_width=True,
        hide_index=True,
    )

    # Rejected compounds
    if rejected_df is not None and not rejected_df.empty:
        with st.expander(f"✗ Rejected Compounds ({n_rejected})", expanded=False):
            st.dataframe(rejected_df, use_container_width=True, hide_index=True)

    # Proceed CTA
    st.divider()
    st.page_link(
        "pages/04_ai_screening.py",
        label="Proceed to AI Screening →",
        icon="🤖",
    )

render_scientific_disclaimer()
