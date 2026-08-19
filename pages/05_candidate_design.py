"""
pages/05_candidate_design.py
-----------------------------
TargetForge — Candidate Design & Property Filtering

Interactive Lipinski/TPSA/RotBonds physicochemical property filtering and candidate generation workspace.
INVARIANT: tf_filter_config (backend defaults) is never overwritten.
           Slider state is stored in tf_ui_filter_config.
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from src.ui.state import init_session_state, WorkflowStep
from src.ui.theme import inject_global_css, badge_html, COLORS
from src.ui.components import (
    render_top_navbar,
    render_horizontal_stepper,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
    render_property_radar,
    render_scientific_metric,
    render_molecule,
)
from src.ui.charts import filter_heatmap, filter_funnel
from src.ui.adapter import reapply_filters, adapt_ranked_df

inject_global_css()
init_session_state(_ROOT)
render_top_navbar()
render_horizontal_stepper(WorkflowStep.DESIGN)
render_step_gate(WorkflowStep.DESIGN)
render_demo_banner()

st.title("Candidate Design & Filtering")
st.caption("Physicochemical property filtering, Lipinski Rule-of-Five compliance, and candidate evaluation.")

# ─── Data ────────────────────────────────────────────────────────────────────
validated_df   = st.session_state.get("tf_validated_df")
backend_config = st.session_state.get("tf_filter_config", {})
ui_config      = st.session_state.get("tf_ui_filter_config") or dict(backend_config)

if validated_df is None or validated_df.empty:
    st.warning("No validated compounds found. Complete the Dataset Manager step.", icon=":material/warning:")
    st.page_link("pages/03_dataset_manager.py", label="← Go to Dataset Manager", icon=":material/database:")
    render_scientific_disclaimer()
    st.stop()

# Need descriptor columns
required_descs = {"molecular_weight", "logp", "hbd", "hba", "tpsa"}
if not required_descs.issubset(set(validated_df.columns)):
    ranked_df = st.session_state.get("tf_ranked_df")
    if ranked_df is not None and required_descs.issubset(set(ranked_df.columns)):
        validated_df = ranked_df
    else:
        st.info(
            "Molecular descriptors are not yet computed. Run the screening pipeline from the Home page.",
            icon=":material/info:",
        )
        st.page_link("pages/01_home.py", label="← Go to Home", icon=":material/home:")
        render_scientific_disclaimer()
        st.stop()

# ─── Two-Column Scientific Layout ───────────────────────────────────────────
col_sliders, col_results = st.columns([1, 2.5], gap="large")

with col_sliders:
    st.markdown("### Filter Parameters")
    st.caption("Adjust thresholds to filter candidate pool in real time.")

    mw_val  = st.slider("Molecular Weight (Da)", 0, 1000,
                         int(ui_config.get("max_molecular_weight", 500)), step=10,
                         key="sl_mw")
    lp_val  = st.slider("LogP", -5.0, 10.0,
                         float(ui_config.get("max_logp", 5.0)), step=0.1,
                         format="%.1f", key="sl_lp")
    hbd_val = st.slider("HBD (H-bond Donors)", 0, 15,
                         int(ui_config.get("max_hbd", 5)), key="sl_hbd")
    hba_val = st.slider("HBA (H-bond Acceptors)", 0, 20,
                         int(ui_config.get("max_hba", 10)), key="sl_hba")
    tps_val = st.slider("TPSA (Å²)", 0, 200,
                         int(ui_config.get("max_tpsa", 140)), step=5, key="sl_tps")
    rb_val  = st.slider("Rotatable Bonds", 0, 20,
                         int(ui_config.get("max_rotatable_bonds", 10)), key="sl_rb")

    if st.button("Reset to Default Filters", key="reset_filters", use_container_width=True):
        for key in ["sl_mw", "sl_lp", "sl_hbd", "sl_hba", "sl_tps", "sl_rb"]:
            if key in st.session_state:
                del st.session_state[key]
        if "tf_ui_filter_config" in st.session_state:
            del st.session_state["tf_ui_filter_config"]
        st.rerun()

# Apply reactive filters
current_ui_config = {
    "max_molecular_weight": mw_val,
    "max_logp":             lp_val,
    "max_hbd":              hbd_val,
    "max_hba":              hba_val,
    "max_tpsa":             tps_val,
    "max_rotatable_bonds":  rb_val,
}
st.session_state["tf_ui_filter_config"] = current_ui_config
filtered_df = reapply_filters(validated_df, current_ui_config)
st.session_state["tf_filtered_df"] = filtered_df

with col_results:
    n_pass     = (filtered_df["filter_status"] == "PASS").sum()
    n_rejected = (filtered_df["filter_status"] == "REJECTED").sum()
    n_total    = len(filtered_df)
    pass_rate  = n_pass / n_total * 100 if n_total > 0 else 0

    st.markdown("### Filtering Assessment")
    m1, m2, m3 = st.columns(3)
    with m1:
        render_scientific_metric("Passing Filter", n_pass, f"{pass_rate:.0f}% of candidate pool")
    with m2:
        render_scientific_metric("Excluded", n_rejected, "Threshold violations")
    with m3:
        render_scientific_metric("Compliance Rate", f"{pass_rate:.1f}%", "Rule-of-Five compliance")

    st.markdown("")

    # High Visual Priority: Results Table
    st.markdown("### Candidate Physicochemical Compliance")
    table_cols = [c for c in [
        "compound_id", "filter_status", "molecular_weight", "logp", "hbd", "hba",
        "tpsa", "rotatable_bonds"
    ] if c in filtered_df.columns]

    disp = filtered_df[table_cols].copy()
    st.dataframe(
        disp.round(3),
        use_container_width=True,
        hide_index=True,
        column_config={
            "compound_id": st.column_config.TextColumn("Compound ID", width="small"),
            "filter_status": st.column_config.TextColumn("Status", width="small"),
            "molecular_weight": st.column_config.NumberColumn("MW (Da)", format="%.1f"),
            "logp": st.column_config.NumberColumn("LogP", format="%.2f"),
            "hbd": st.column_config.NumberColumn("HBD", format="%d"),
            "hba": st.column_config.NumberColumn("HBA", format="%d"),
            "tpsa": st.column_config.NumberColumn("TPSA (Å²)", format="%.1f"),
            "rotatable_bonds": st.column_config.NumberColumn("Rot. Bonds", format="%d"),
        },
    )

    with st.expander("Compliance Heatmap Matrix", expanded=False):
        st.plotly_chart(filter_heatmap(filtered_df, current_ui_config), use_container_width=True)

# ─── Dense Candidate Structure Cards ─────────────────────────────────────────
st.divider()
st.markdown("### Candidate Structural Evaluation")
st.caption("2D chemical structures, bioactivity predictions, and physicochemical descriptors of eligible leads.")

candidates = st.session_state.get("tf_candidates")
if candidates:
    cols_per_row = 3
    for i in range(0, len(candidates), cols_per_row):
        row_cands = candidates[i : i + cols_per_row]
        c_cols = st.columns(cols_per_row, gap="medium")
        for j, cand in enumerate(row_cands):
            with c_cols[j]:
                fstat = cand.filter.status
                badge_k = "pass" if fstat == "PASS" else "rejected"
                
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #D9E2EC; border-radius:8px; padding:14px; margin-bottom:12px; box-shadow:0 1px 2px rgba(16,42,67,0.03);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; border-bottom:1px solid #EEF2F6; padding-bottom:6px;">
                            <span style="font-weight:700; color:#102A43; font-size:14px;">{cand.candidate_id}</span>
                            <span class="tf-badge tf-badge-{badge_k}">{fstat}</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                render_molecule(cand.smiles, width=220, height=130)
                st.markdown(
                    f"""
                        <div style="margin-top:8px; font-size:12px; line-height:1.6;">
                            <div style="display:flex; justify-content:space-between;"><span style="color:#52606D;">Activity Score:</span> <strong style="color:#102A43;">{cand.activity_score:.3f}</strong></div>
                            <div style="display:flex; justify-content:space-between;"><span style="color:#52606D;">Novelty Score:</span> <strong style="color:#102A43;">{cand.novelty_score:.2f}</strong></div>
                            <div style="display:flex; justify-content:space-between;"><span style="color:#52606D;">MW / LogP:</span> <span style="color:#102A43;">{cand.properties.mw:.1f} Da / {cand.properties.logp:.2f}</span></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ─── Proceed CTA ─────────────────────────────────────────────────────────────
st.divider()
if st.button("Confirm Eligible Candidates & Proceed to Docking Analysis →", type="primary"):
    st.page_link("pages/06_docking_analysis.py", label="Proceed to Docking Analysis →", icon=":material/join_inner:")
    st.success("Candidate set confirmed.")

render_scientific_disclaimer()
