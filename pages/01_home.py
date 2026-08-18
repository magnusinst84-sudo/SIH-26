"""
pages/01_home.py
----------------
TargetForge — Home Page

Landing page with hero section, pipeline CTA, and results summary.
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys
import time

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from src.ui.state import init_session_state, populate_from_pipeline
from src.ui.theme import inject_global_css
from src.ui.components import (
    render_sidebar_progress,
    render_scientific_disclaimer,
    render_demo_banner,
    render_kpi_row,
    render_loading_stages,
)
from src.ui.charts import score_bar_chart

# Ensure state and CSS are initialised (idempotent)
inject_global_css()
init_session_state(_ROOT)
render_sidebar_progress()

# ─── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
  <h1>🧬 TargetForge</h1>
  <p>AI-assisted target-specific virtual screening for drug discovery</p>
  <span class="hero-badge">COVID-19</span>
  <span class="hero-badge">SARS-CoV-2 Mpro</span>
  <span class="hero-badge">PDB: 6LU7</span>
  <span class="hero-badge">Hackathon Prototype</span>
</div>
""", unsafe_allow_html=True)

# ─── One-shot demo pipeline trigger ─────────────────────────────────────────
pipeline_ran = st.session_state.get("tf_pipeline_ran", False)
candidates   = st.session_state.get("tf_candidates")

col_run, col_step = st.columns([1, 1], gap="large")

with col_run:
    run_btn = st.button(
        "🚀 Run Full Demo Screening",
        type="primary",
        use_container_width=True,
        help="Run the complete TargetForge demo pipeline end-to-end.",
    )

with col_step:
    st.page_link(
        "pages/02_target_explorer.py",
        label="→ Start step-by-step workflow",
        icon="🎯",
    )

if run_btn:
    stages = [
        "Loading compound library",
        "Validating SMILES structures",
        "Calculating molecular descriptors",
        "Predicting biological activity",
        "Applying property filters",
        "Running docking simulation (fallback)",
        "Ranking and scoring candidates",
    ]
    stage_container = st.empty()
    with st.spinner("Running TargetForge demonstration pipeline…"):
        from src.pipeline.run_demo import run_demo  # M2 — unchanged call
        for idx in range(len(stages)):
            with stage_container.container():
                render_loading_stages(stages, idx)
            time.sleep(0.18)
        ranked_df = run_demo(_ROOT)
        populate_from_pipeline(_ROOT, ranked_df)

    stage_container.empty()
    st.success("✅ Screening complete! Results are ready.")
    st.rerun()

# ─── Results view ────────────────────────────────────────────────────────────
candidates = st.session_state.get("tf_candidates")

if candidates:
    render_demo_banner()
    render_kpi_row(candidates)
    st.markdown("")

    tab_chart, tab_info = st.tabs(["📊 Score Summary", "ℹ️ About This Run"])
    with tab_chart:
        st.plotly_chart(score_bar_chart(candidates), use_container_width=True)
        st.page_link("pages/07_final_ranking.py", label="View Full Ranking →", icon="🏆")

    with tab_info:
        target = st.session_state.get("tf_target", {})
        weights = st.session_state.get("tf_weights", {})
        st.markdown(f"""
| Field | Value |
|---|---|
| Disease | {target.get('disease','N/A')} |
| Target | {target.get('name','N/A')} |
| PDB Structure | {target.get('structure_id','N/A')} |
| Model | {target.get('model_version','demo_v1')} |
| Ranking weights | Activity {weights.get('activity_weight',0.4):.0%} / Docking {weights.get('docking_weight',0.3):.0%} / Property {weights.get('property_weight',0.2):.0%} / Novelty {weights.get('novelty_weight',0.1):.0%} |
""")

else:
    # No data yet — show workflow overview
    st.info(
        "👆 Click **Run Full Demo Screening** to execute the TargetForge pipeline, "
        "or use the step-by-step workflow to proceed stage by stage.",
        icon="ℹ️",
    )
    st.markdown("### Workflow Steps")
    steps_info = [
        ("🎯", "Target Explorer",   "Review the biological target and scoring configuration."),
        ("📂", "Dataset Manager",   "Load the demo compound library or upload a custom CSV."),
        ("🤖", "AI Screening",      "Review activity predictions for all validated compounds."),
        ("🧪", "Candidate Design",  "Apply interactive Lipinski/TPSA filters to narrow candidates."),
        ("⚛️", "Docking Analysis",  "Inspect docking scores (fallback demo values)."),
        ("🏆", "Final Ranking",     "View the official ranking and explore what-if weight scenarios."),
        ("📄", "Reports",           "Export results as CSV, Markdown, or JSON."),
    ]
    cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(steps_info):
        with cols[i % 2]:
            st.markdown(
                f'<div class="tf-card-sm"><strong>{icon} {title}</strong>'
                f'<br><span style="color:#52606D;font-size:0.88rem">{desc}</span></div>',
                unsafe_allow_html=True,
            )

render_scientific_disclaimer()
