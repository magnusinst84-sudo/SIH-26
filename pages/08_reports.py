"""
pages/08_reports.py
-------------------
TargetForge — Reports

Configurable screening report generator and multi-format export tools (CSV, Markdown, JSON).
Scientific Limitations notice is always included.
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.ui.state import init_session_state, WorkflowStep
from src.ui.theme import inject_global_css, badge_html, COLORS
from src.ui.components import (
    render_top_navbar,
    render_horizontal_stepper,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
    render_scientific_metric,
)
from src.ui.export import (
    build_ranking_csv,
    build_validated_csv,
    build_markdown_report,
    build_summary_json,
)

inject_global_css()
init_session_state(_ROOT)
render_top_navbar()
render_horizontal_stepper(WorkflowStep.REPORTS)
render_step_gate(WorkflowStep.REPORTS)
render_demo_banner()

st.title("Screening Reports & Exports")
st.caption("Generate comprehensive computational discovery reports and download structured data artifacts.")

# ─── 1. Report Status Summary ────────────────────────────────────────────────
state_snapshot = dict(st.session_state)
candidates     = state_snapshot.get("tf_candidates") or []
validated_df   = state_snapshot.get("tf_validated_df")
target         = state_snapshot.get("tf_target", {})

r1, r2, r3, r4 = st.columns(4)
with r1:
    render_scientific_metric("Target", target.get("structure_id", "6LU7"), target.get("name", "SARS-CoV-2 Mpro"))
with r2:
    render_scientific_metric("Screened Cohort", len(validated_df) if validated_df is not None else 0, "Ingested molecules")
with r3:
    render_scientific_metric("Prioritized Leads", len(candidates), "Docked & ranked leads")
with r4:
    render_scientific_metric("Pipeline Status", "Complete", "Ready for export")

st.markdown("")

# ─── 2. Report Configuration ─────────────────────────────────────────────────
st.markdown("### Report Section Configuration")
st.caption("Select sections to compile into the discovery dossier. **Scientific Notice** is mandatory.")

col_a, col_b = st.columns(2)
with col_a:
    inc_target   = st.checkbox("Target Specification & Structural Profile", value=True)
    inc_dataset  = st.checkbox("Chemical Library Ingestion & Quality Metrics", value=True)
    inc_screen   = st.checkbox("AI Bioactivity Screening Summary", value=True)
with col_b:
    inc_filter   = st.checkbox("Physicochemical Property Filter Compliance", value=True)
    inc_docking  = st.checkbox("Structure-Based Docking Affinities", value=True)
    inc_ranking  = st.checkbox("Lead Candidate Prioritization Table", value=True)

sections = []
if inc_target:  sections.append("target")
if inc_dataset: sections.append("dataset")
if inc_screen:  sections.append("screening")
if inc_filter:  sections.append("filter")
if inc_docking: sections.append("docking")
if inc_ranking: sections.append("ranking")
sections.append("disclaimer")   # mandatory

# ─── 3. Report Preview ───────────────────────────────────────────────────────
st.markdown("### Report Document Preview")
report_md = build_markdown_report(state_snapshot, sections)
with st.expander("Expand Markdown Document Preview", expanded=True):
    st.markdown(report_md)

# ─── 4. Export Artifacts ─────────────────────────────────────────────────────
st.markdown("### Download Data Artifacts")
st.caption("Export structured CSV datasets, executive markdown summaries, or JSON pipeline snapshots.")

dl1, dl2, dl3, dl4 = st.columns(4)

with dl1:
    csv_data = build_ranking_csv(candidates)
    st.download_button(
        "Lead Ranking (CSV)",
        data      = csv_data,
        file_name = "targetforge_lead_ranking.csv",
        mime      = "text/csv",
        use_container_width = True,
    )

with dl2:
    val_csv = build_validated_csv(validated_df)
    st.download_button(
        "Library Descriptors (CSV)",
        data      = val_csv,
        file_name = "targetforge_library_descriptors.csv",
        mime      = "text/csv",
        use_container_width = True,
    )

with dl3:
    st.download_button(
        "Discovery Dossier (MD)",
        data      = report_md,
        file_name = "targetforge_discovery_report.md",
        mime      = "text/markdown",
        use_container_width = True,
    )

with dl4:
    json_data = build_summary_json(state_snapshot)
    st.download_button(
        "Pipeline State (JSON)",
        data      = json_data,
        file_name = "targetforge_pipeline_state.json",
        mime      = "application/json",
        use_container_width = True,
    )

# ─── 5. Data Completeness Checklist ──────────────────────────────────────────
st.divider()
st.markdown("### Workflow Data Completeness")
checks = [
    ("Target configured",       state_snapshot.get("tf_target") is not None),
    ("Dataset loaded",          state_snapshot.get("tf_validated_df") is not None),
    ("Screening results",       state_snapshot.get("tf_predicted_df") is not None),
    ("Filter results",          state_snapshot.get("tf_filtered_df") is not None),
    ("Docking results",         state_snapshot.get("tf_docked_df") is not None),
    ("Ranking complete",        state_snapshot.get("tf_ranked_df") is not None),
    ("Demonstration mode",      state_snapshot.get("tf_demo_mode", True)),
]
for label, ok in checks:
    dot = '<span style="color:#0F766E; margin-right: 8px; font-weight: 700;">✓</span>' if ok else '<span style="color:#94A3B8; margin-right: 8px;">○</span>'
    st.markdown(f'<div style="font-size:13px; color:#243B53; padding: 3px 0; display: flex; align-items: center;">{dot} {label}</div>', unsafe_allow_html=True)

render_scientific_disclaimer()
