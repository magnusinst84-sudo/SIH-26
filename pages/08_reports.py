"""
pages/08_reports.py
-------------------
TargetForge — Reports

Generate and download exportable summaries.
Scientific Limitations section is always included.
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.ui.state import init_session_state, WorkflowStep
from src.ui.theme import inject_global_css
from src.ui.components import (
    render_sidebar_progress,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
)
from src.ui.export import (
    build_ranking_csv,
    build_validated_csv,
    build_markdown_report,
    build_summary_json,
)

inject_global_css()
init_session_state(_ROOT)
render_sidebar_progress()
render_step_gate(WorkflowStep.REPORTS)
render_demo_banner()

st.title("📄 Reports")
st.caption("Configure and download screening results in multiple formats.")

# ─── Report section toggles ──────────────────────────────────────────────────
st.markdown("### Report Sections")
st.caption("Select sections to include. **Scientific Limitations** is always included.")

col_a, col_b = st.columns(2)
with col_a:
    inc_target   = st.checkbox("🎯 Target Summary",     value=True)
    inc_dataset  = st.checkbox("📂 Dataset Statistics", value=True)
    inc_screen   = st.checkbox("🤖 AI Screening Summary", value=True)
with col_b:
    inc_filter   = st.checkbox("🧪 Filter Results",     value=True)
    inc_docking  = st.checkbox("⚛️ Docking Results",    value=True)
    inc_ranking  = st.checkbox("🏆 Final Ranking Table", value=True)

sections = []
if inc_target:  sections.append("target")
if inc_dataset: sections.append("dataset")
if inc_screen:  sections.append("screening")
if inc_filter:  sections.append("filter")
if inc_docking: sections.append("docking")
if inc_ranking: sections.append("ranking")
sections.append("disclaimer")   # always

# ─── Snapshot of current session state ───────────────────────────────────────
state_snapshot = dict(st.session_state)

# ─── Report preview ──────────────────────────────────────────────────────────
st.divider()
st.markdown("### Preview")
with st.expander("📋 Report Preview (Markdown)", expanded=True):
    report_md = build_markdown_report(state_snapshot, sections)
    st.markdown(report_md)

# ─── Export buttons ───────────────────────────────────────────────────────────
st.divider()
st.markdown("### Download")
candidates   = state_snapshot.get("tf_candidates")  or []
validated_df = state_snapshot.get("tf_validated_df")

dl1, dl2, dl3, dl4 = st.columns(4)

with dl1:
    csv_data = build_ranking_csv(candidates)
    st.download_button(
        "⬇ Ranking CSV",
        data    = csv_data,
        file_name = "targetforge_ranking.csv",
        mime    = "text/csv",
        use_container_width = True,
    )

with dl2:
    val_csv = build_validated_csv(validated_df)
    st.download_button(
        "⬇ Validated CSV",
        data    = val_csv,
        file_name = "targetforge_validated.csv",
        mime    = "text/csv",
        use_container_width = True,
    )

with dl3:
    st.download_button(
        "⬇ Full Report (Markdown)",
        data    = report_md,
        file_name = "targetforge_report.md",
        mime    = "text/markdown",
        use_container_width = True,
    )

with dl4:
    json_data = build_summary_json(state_snapshot)
    st.download_button(
        "⬇ Summary JSON",
        data    = json_data,
        file_name = "targetforge_summary.json",
        mime    = "application/json",
        use_container_width = True,
    )

# ─── Data completeness notice ────────────────────────────────────────────────
st.divider()
st.markdown("### Data Availability")
checks = [
    ("Target configured",       state_snapshot.get("tf_target") is not None),
    ("Dataset loaded",          state_snapshot.get("tf_validated_df") is not None),
    ("Screening results",       state_snapshot.get("tf_predicted_df") is not None),
    ("Filter results",          state_snapshot.get("tf_filtered_df") is not None),
    ("Docking results",         state_snapshot.get("tf_docked_df") is not None),
    ("Ranking complete",        state_snapshot.get("tf_ranked_df") is not None),
    ("Demo mode",               state_snapshot.get("tf_demo_mode", True)),
]
for label, ok in checks:
    icon = "✅" if ok else "⬜"
    st.markdown(f"{icon} {label}")

render_scientific_disclaimer()
