"""
pages/05_candidate_design.py
-----------------------------
TargetForge — Candidate Design

Interactive Lipinski/TPSA/RotBonds property filtering.
Slider changes re-filter the candidate set in real time.
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
)
from src.ui.charts import filter_heatmap, filter_funnel
from src.ui.adapter import reapply_filters, adapt_ranked_df

inject_global_css()
init_session_state(_ROOT)
render_top_navbar()
render_horizontal_stepper(WorkflowStep.DESIGN)
render_step_gate(WorkflowStep.DESIGN)
render_demo_banner()

st.title("Candidate Design")
st.caption("Apply interactive property filters to narrow your candidate set.")

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
    # Try to use ranked_df which has descriptors
    ranked_df = st.session_state.get("tf_ranked_df")
    if ranked_df is not None and required_descs.issubset(set(ranked_df.columns)):
        validated_df = ranked_df
    else:
        st.info(
            "Molecular descriptors are not yet computed. "
            "Run the full demo pipeline from the Home page to populate descriptor columns.",
            icon=":material/info:",
        )
        st.page_link("pages/01_home.py", label="← Go to Home", icon=":material/home:")
        render_scientific_disclaimer()
        st.stop()

# ─── Filter Sliders (left panel) ─────────────────────────────────────────────
col_sliders, col_results = st.columns([1, 2.5], gap="large")

with col_sliders:
    st.markdown("### Filter Thresholds")
    st.caption("Drag sliders to filter compounds in real time.")

    mw_val  = st.slider("Molecular Weight (Da)", 0, 1000,
                         int(ui_config.get("max_molecular_weight", 500)), step=10,
                         key="sl_mw")
    lp_val  = st.slider("LogP", -5.0, 10.0,
                         float(ui_config.get("max_logp", 5.0)), step=0.1,
                         format="%.1f", key="sl_lp")
    hbd_val = st.slider("HBD (H-bond donors)", 0, 15,
                         int(ui_config.get("max_hbd", 5)), key="sl_hbd")
    hba_val = st.slider("HBA (H-bond acceptors)", 0, 20,
                         int(ui_config.get("max_hba", 10)), key="sl_hba")
    tps_val = st.slider("TPSA (Å²)", 0, 200,
                         int(ui_config.get("max_tpsa", 140)), step=5, key="sl_tps")
    rb_val  = st.slider("Rotatable Bonds", 0, 20,
                         int(ui_config.get("max_rotatable_bonds", 10)), key="sl_rb")
    st.caption("Rotatable Bonds threshold is a UI-only parameter — not in `filters.yaml`.")

    if st.button("Reset to Backend Defaults", key="reset_filters"):
        for key in ["sl_mw", "sl_lp", "sl_hbd", "sl_hba", "sl_tps", "sl_rb"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.divider()
    st.markdown("**Backend Defaults** (`filters.yaml`)")
    for label, val in [
        ("MW ≤",   f"{backend_config.get('max_molecular_weight',500)} Da"),
        ("LogP ≤", f"{backend_config.get('max_logp', 5.0)}"),
        ("HBD ≤",  f"{backend_config.get('max_hbd', 5)}"),
        ("HBA ≤",  f"{backend_config.get('max_hba', 10)}"),
        ("TPSA ≤", f"{backend_config.get('max_tpsa', 140)} Å²"),
    ]:
        c1, c2 = st.columns(2)
        c1.caption(label)
        c2.caption(val)

# ─── Build current UI config and apply filters (reactive) ────────────────────
current_ui_config = {
    "max_molecular_weight": mw_val,
    "max_logp":             lp_val,
    "max_hbd":              hbd_val,
    "max_hba":              hba_val,
    "max_tpsa":             tps_val,
    "max_rotatable_bonds":  rb_val,
}
# Update session state on every render (slider change triggers rerun)
st.session_state["tf_ui_filter_config"] = current_ui_config
filtered_df = reapply_filters(validated_df, current_ui_config)
st.session_state["tf_filtered_df"] = filtered_df

# ─── Results Panel ───────────────────────────────────────────────────────────
with col_results:
    n_pass     = (filtered_df["filter_status"] == "PASS").sum()
    n_rejected = (filtered_df["filter_status"] == "REJECTED").sum()
    n_total    = len(filtered_df)
    pass_rate  = n_pass / n_total * 100 if n_total > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("PASS",       n_pass)
    m2.metric("Rejected",   n_rejected)
    m3.metric("Pass Rate",  f"{pass_rate:.0f}%")

    st.plotly_chart(filter_heatmap(filtered_df, current_ui_config), use_container_width=True)
    st.plotly_chart(
        filter_funnel(n_total, n_pass, n_rejected),
        use_container_width=True,
    )

    # Full results table
    st.markdown("#### Filter Results")
    table_cols = [c for c in [
        "compound_id", "molecular_weight", "logp", "hbd", "hba",
        "tpsa", "rotatable_bonds", "filter_status", "filter_reasons",
    ] if c in filtered_df.columns]

    disp = filtered_df[table_cols].copy()
    if "filter_status" in disp.columns:
        disp.insert(0, "Status", disp["filter_status"].map(
            {"PASS": "PASS", "REJECTED": "REJECTED"}
        ))
    st.dataframe(
        disp.round(3),
        use_container_width=True,
        hide_index=True,
        column_config={
            "molecular_weight": st.column_config.NumberColumn("MW (Da)", format="%.1f"),
            "logp":  st.column_config.NumberColumn("LogP",  format="%.3f"),
            "tpsa":  st.column_config.NumberColumn("TPSA",  format="%.1f"),
        },
    )

    # Rejected breakdown
    rejected_rows = filtered_df[filtered_df["filter_status"] == "REJECTED"]
    if not rejected_rows.empty:
        with st.expander(f"Rejected compounds ({len(rejected_rows)})", expanded=False):
            for _, row in rejected_rows.iterrows():
                reasons = row.get("filter_reasons", "")
                st.markdown(
                    f"**{row.get('compound_id','')}** — {reasons or 'See threshold values'}"
                )

# ─── Property radar for each candidate ───────────────────────────────────────
st.divider()
st.markdown("### Molecular Property Profiles")
candidates = st.session_state.get("tf_candidates")
if candidates:
    radar_cols = st.columns(min(3, len(candidates)))
    for i, cand in enumerate(candidates):
        with radar_cols[i % 3]:
            render_property_radar(cand, current_ui_config,
                                  title=cand.candidate_id)
else:
    st.caption("Run the full pipeline from Home to see property radar charts.")

# ─── Proceed CTA ─────────────────────────────────────────────────────────────
st.divider()
if n_pass == 0:
    st.warning("No compounds pass the current filters. Adjust thresholds to proceed.", icon=":material/warning:")
else:
    st.success(f"{n_pass} compound(s) pass filters and are eligible for docking.")
    st.page_link(
        "pages/06_docking_analysis.py",
        label="Proceed to Docking Analysis →",
        icon=":material/join_inner:",
    )

render_scientific_disclaimer()
